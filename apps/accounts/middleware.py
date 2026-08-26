"""
Rate Limiting Middleware for AttendX Authentication.

Prevents brute-force attacks on the login endpoint by locking out an
IP address after too many consecutive failed attempts. Failed attempts
are recorded by AuthService.record_failed_login() (called from the
login view); this middleware rejects requests while a lockout is active.
"""

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from apps.accounts.services import AuthService


class LoginRateLimitMiddleware(MiddlewareMixin):
    """Reject login attempts from IPs that are currently locked out."""

    def process_request(self, request):
        # Only apply to the faculty login endpoint.
        if request.path != '/accounts/login/' or request.method != 'POST':
            return None

        ip_address = self.get_client_ip(request)
        if AuthService.is_locked_out(ip_address):
            lockout_minutes = getattr(settings, 'ATTENDX_LOCKOUT_DURATION_MINUTES', 15)
            messages.error(
                request,
                f'Too many failed login attempts. Please try again in {lockout_minutes} minutes.',
            )
            return redirect('accounts:login')

        return None

    @staticmethod
    def get_client_ip(request):
        """Extract the client IP, honoring X-Forwarded-For for proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
