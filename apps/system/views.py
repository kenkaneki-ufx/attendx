from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import sys
import django


class SystemSettingsView(LoginRequiredMixin, TemplateView):
    """View for system settings (admin only)."""
    template_name = 'system/settings.html'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            from django.http import Http404
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from apps.accounts.models import Faculty
        from apps.students.models import Student
        from apps.departments.models import Department
        from apps.subjects.models import Subject
        from apps.lectures.models import Lecture
        from apps.attendance.models import AttendanceRecord

        # System statistics
        context['stats'] = {
            'total_faculty': Faculty.objects.count(),
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_departments': Department.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_lectures': Lecture.objects.count(),
            'total_attendance': AttendanceRecord.objects.count(),
        }

        # Configuration settings
        context['settings'] = {
            'qr_expiry': getattr(settings, 'ATTENDX_QR_EXPIRY_SECONDS', 60),
            'max_login_attempts': getattr(settings, 'ATTENDX_MAX_LOGIN_ATTEMPTS', 5),
            'lockout_duration': getattr(settings, 'ATTENDX_LOCKOUT_DURATION_MINUTES', 15),
            'portal_rate_limit': 10,
            'email_backend': settings.EMAIL_BACKEND.split('.')[-1],
            'email_host': getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
            'email_port': getattr(settings, 'EMAIL_PORT', 587),
            'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'AttendX <noreply@attendx.com>'),
            'django_version': django.VERSION[:3],
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'db_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
            'debug': settings.DEBUG,
            'timezone': settings.TIME_ZONE,
            'cache_backend': settings.CACHES['default']['BACKEND'].split('.')[-1],
            'csrf_enabled': 'CsrfViewMiddleware' in settings.MIDDLEWARE,
            'xss_filter': getattr(settings, 'SECURITY_BROWSER_XSS_FILTER', False),
            'https_only': not settings.DEBUG,
            'secure_hsts': getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
        }

        return context
