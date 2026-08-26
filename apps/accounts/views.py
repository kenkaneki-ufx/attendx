"""Views for the accounts app (faculty authentication).

Implement the full authentication flow:
  - Login with per-IP rate limiting
  - Logout (POST preferred, GET supported for legacy links)
  - Profile view/edit
  - Change password
  - Forgot password (sends a real reset email)
  - Reset password (validates token, sets new password)
"""
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.accounts.forms import (
    ChangePasswordForm,
    FacultyLoginForm,
    FacultyProfileForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from apps.accounts.services import AuthService


class FacultyLoginView(LoginView):
    """Faculty login view with brute-force rate limiting."""

    form_class = FacultyLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:faculty_dashboard')

    @staticmethod
    def _client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    def form_valid(self, form):
        # LoginView.form_valid performs the actual auth_login via form.get_user().
        AuthService.clear_failed_logins(self._client_ip(self.request))
        messages.success(self.request, f'Welcome back, {form.get_user().get_full_name()}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        AuthService.record_failed_login(self._client_ip(self.request))
        return super().form_invalid(form)


class FacultyLogoutView(LoginRequiredMixin, View):
    """Logout view. Prefers POST (CSRF-safe); GET kept for legacy links."""

    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """View for displaying and editing the faculty profile."""

    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FacultyProfileForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form = FacultyProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """Change the current user's password."""

    template_name = 'accounts/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        success, message = AuthService.change_password(
            self.request.user,
            form.cleaned_data['old_password'],
            form.cleaned_data['new_password'],
        )
        if success:
            messages.success(self.request, message)
            return super().form_valid(form)
        messages.error(self.request, message)
        return self.form_invalid(form)


class ForgotPasswordView(FormView):
    """Request a password reset email.

    Always shows the same success message (whether or not the account
    exists) to prevent user-enumeration.
    """

    template_name = 'accounts/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('accounts:forgot_password')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = AuthService.get_user_by_email(email)
        if user is not None:
            uidb64, token = AuthService.get_reset_link(user)
            AuthService.send_password_reset_email(user, uidb64, token)
        messages.success(
            self.request,
            'If an account exists with this email, you will receive a password reset link.',
        )
        return super().form_valid(form)


class ResetPasswordView(FormView):
    """Validate the reset token and set a new password."""

    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('accounts:login')

    def get_user(self):
        """Decode the uidb64 from the URL (None if invalid)."""
        return AuthService.user_from_uidb64(self.kwargs.get('uidb64'))

    def get(self, request, *args, **kwargs):
        user = self.get_user()
        token = self.kwargs.get('token', '')
        if user is None or not AuthService.is_reset_token_valid(user, token):
            messages.error(request, 'This reset link is invalid or has expired.')
            return redirect('accounts:forgot_password')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.get_user()
        token = self.kwargs.get('token', '')
        if user is None:
            messages.error(self.request, 'This reset link is invalid or has expired.')
            return redirect('accounts:forgot_password')
        success, message = AuthService.reset_password(
            user, token, form.cleaned_data['new_password']
        )
        if success:
            messages.success(self.request, message)
            return super().form_valid(form)
        messages.error(self.request, message)
        return redirect('accounts:forgot_password')
