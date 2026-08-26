from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(TemplateView):
    """
    Home page view.
    - Unauthenticated users see the landing page
    - Authenticated users are redirected to the dashboard
    """
    template_name = 'core/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:faculty_dashboard')
        return super().dispatch(request, *args, **kwargs)


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """Redirect to the appropriate dashboard based on user role."""
    login_url = '/accounts/login/'

    def get(self, request, *args, **kwargs):
        return redirect('dashboard:faculty_dashboard')
