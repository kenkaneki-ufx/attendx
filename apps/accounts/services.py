"""Service layer for authentication-related operations.

Keeps business logic out of views so it is testable and reusable.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

Faculty = get_user_model()


class AuthService:
    """Authentication and account-management operations."""

    # ------------------------------------------------------------------
    # Password change
    # ------------------------------------------------------------------
    @staticmethod
    def change_password(user, old_password, new_password):
        """Change a user's password after verifying the current one."""
        if not user.check_password(old_password):
            return False, 'Current password is incorrect.'
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return True, 'Password changed successfully.'

    # ------------------------------------------------------------------
    # Password reset (forgot password)
    # ------------------------------------------------------------------
    @staticmethod
    def get_user_by_email(email):
        """Look up an active user by email (returns None if not found)."""
        try:
            return Faculty.objects.get(email__iexact=email, is_active=True)
        except Faculty.DoesNotExist:
            return None

    @staticmethod
    def get_reset_link(user):
        """Build the password-reset URL for a user.

        Returns (uidb64, token) that the reset view can consume.
        """
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uidb64, token

    @staticmethod
    def send_password_reset_email(user, uidb64, token):
        """Email the password reset link to the user.

        Uses the configured EMAIL_BACKEND (console in dev, SMTP in prod).
        """
        subject = 'Reset your AttendX password'
        reset_url = ('{}/accounts/reset-password/{}/{}/'.format(
            settings.PASSWORD_RESET_BASE_URL.rstrip('/'),
            uidb64,
            token,
        ))
        message = render_to_string('accounts/emails/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'AttendX',
        })
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    @staticmethod
    def user_from_uidb64(uidb64):
        """Decode uidb64 into a user (None if malformed or missing)."""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return Faculty.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Faculty.DoesNotExist):
            return None

    @staticmethod
    def is_reset_token_valid(user, token):
        """Whether the reset token is currently valid for the user."""
        return default_token_generator.check_token(user, token)

    @staticmethod
    def reset_password(user, token, new_password):
        """Validate the reset token and set a new password.

        Returns (success: bool, message: str).
        """
        if not default_token_generator.check_token(user, token):
            return False, 'This reset link is invalid or has expired. Please request a new one.'
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return True, 'Your password has been reset successfully. '
        'You can now log in with your new password.'

    # ------------------------------------------------------------------
    # Login rate limiting
    # ------------------------------------------------------------------
    @staticmethod
    def _attempt_key(ip):
        return f'login_attempts_{ip}'

    @staticmethod
    def _lockout_key(ip):
        return f'login_lockout_{ip}'

    @classmethod
    def get_attempts(cls, ip):
        """Number of recorded failed attempts for an IP."""
        return cache.get(cls._attempt_key(ip), 0)

    @classmethod
    def record_failed_login(cls, ip):
        """Increment the failure counter and enforce lockout if over the limit."""
        max_attempts = getattr(settings, 'ATTENDX_MAX_LOGIN_ATTEMPTS', 5)
        lockout_minutes = getattr(settings, 'ATTENDX_LOCKOUT_DURATION_MINUTES', 15)

        attempts = cls.get_attempts(ip) + 1
        # Counter TTL equals the lockout so the slate is wiped when it expires.
        cache.set(cls._attempt_key(ip), attempts, timeout=lockout_minutes * 60)

        if attempts >= max_attempts:
            cache.set(cls._lockout_key(ip), True, timeout=lockout_minutes * 60)

    @classmethod
    def clear_failed_logins(cls, ip):
        """Reset all login counters after a successful login."""
        cache.delete(cls._attempt_key(ip))
        cache.delete(cls._lockout_key(ip))

    @classmethod
    def is_locked_out(cls, ip):
        """Whether the IP is currently locked out."""
        return cache.get(cls._lockout_key(ip), False) is True
