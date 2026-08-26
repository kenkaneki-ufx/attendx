from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import qrcode
import io
import base64


class GenerateQRView(LoginRequiredMixin, TemplateView):
    """View for generating QR codes for active lectures."""
    template_name = 'qr_codes/generate.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user

        from apps.lectures.models import Lecture
        from apps.qr_codes.models import QRCodeSession

        active_lecture = Lecture.objects.filter(
            faculty=user,
            lecture_date=today,
            status='IN_PROGRESS',
            is_active=True
        ).select_related('subject', 'section').first()

        context['active_lecture'] = active_lecture

        if active_lecture:
            # Get active QR session (don't auto-create)
            qr_session = QRCodeSession.objects.filter(
                lecture=active_lecture,
                is_active=True
            ).first()

            # Check if session exists and is not expired
            if qr_session and not qr_session.is_expired():
                context['qr_session'] = qr_session
                context['qr_expired'] = False

                # Generate QR image as base64
                qr_url = f"{self.request.scheme}://{self.request.get_host()}/attendance/scan/{qr_session.token}/"
                qr_img = qrcode.make(qr_url)
                buffer = io.BytesIO()
                qr_img.save(buffer, format='PNG')
                qr_b64 = base64.b64encode(buffer.getvalue()).decode()
                context['qr_image'] = qr_b64

                # Calculate remaining time
                remaining = (qr_session.expires_at - timezone.now()).total_seconds()
                context['remaining_seconds'] = max(0, int(remaining))
                context['expiry_time'] = qr_session.expires_at.isoformat()
            else:
                # No active QR or expired - show expired state
                context['qr_session'] = qr_session
                context['qr_expired'] = True
                context['remaining_seconds'] = 0
                if qr_session:
                    context['expiry_time'] = qr_session.expires_at.isoformat()

        return context


class QRDisplayView(LoginRequiredMixin, TemplateView):
    """View for displaying the QR code full screen."""
    template_name = 'qr_codes/qr_display.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        from apps.lectures.models import Lecture
        active_lecture = Lecture.objects.filter(
            faculty=self.request.user,
            lecture_date=today,
            status='IN_PROGRESS',
            is_active=True
        ).first()
        if active_lecture:
            from apps.qr_codes.models import QRCodeSession
            import qrcode, io, base64
            qr_session = QRCodeSession.objects.filter(
                lecture=active_lecture, is_active=True
            ).first()
            if qr_session:
                qr_url = f"{self.request.scheme}://{self.request.get_host()}/attendance/scan/{qr_session.token}/"
                qr_img = qrcode.make(qr_url)
                buffer = io.BytesIO()
                qr_img.save(buffer, format='PNG')
                context['qr_image'] = base64.b64encode(buffer.getvalue()).decode()
        return context


@login_required
@require_POST
def qr_regenerate_api(request):
    """AJAX endpoint to regenerate QR code."""
    today = timezone.now().date()
    from apps.lectures.models import Lecture
    from apps.qr_codes.models import QRCodeSession
    from apps.subjects.models import Subject
    from apps.sections.models import Section
    import qrcode
    import io
    import base64
    import traceback

    try:
        # First, try to find an active lecture
        active_lecture = Lecture.objects.filter(
            faculty=request.user,
            lecture_date=today,
            status='IN_PROGRESS',
            is_active=True
        ).first()

        # If no active lecture, try to find a recent one (within 2 hours) that was completed
        if not active_lecture:
            two_hours_ago = timezone.now() - timezone.timedelta(hours=2)
            recent_lecture = Lecture.objects.filter(
                faculty=request.user,
                lecture_date=today,
                status='COMPLETED',
                is_active=True,
                end_time__gte=two_hours_ago
            ).order_by('-end_time').first()
            
            if recent_lecture:
                # Reactivate the lecture
                recent_lecture.status = 'IN_PROGRESS'
                recent_lecture.end_time = None
                recent_lecture.save(update_fields=['status', 'end_time'])
                active_lecture = recent_lecture

        # If still no lecture, check if there's any lecture today and use the first one
        if not active_lecture:
            any_lecture_today = Lecture.objects.filter(
                faculty=request.user,
                lecture_date=today,
                is_active=True
            ).order_by('-start_time').first()
            
            if any_lecture_today:
                # Reactivate this lecture
                any_lecture_today.status = 'IN_PROGRESS'
                any_lecture_today.end_time = None
                any_lecture_today.save(update_fields=['status', 'end_time'])
                active_lecture = any_lecture_today

        if not active_lecture:
            return JsonResponse({
                'success': False,
                'message': 'No lecture found for today. Please start a new lecture from the dashboard.'
            })

        # Deactivate any existing active sessions for this lecture
        QRCodeSession.objects.filter(
            lecture=active_lecture, is_active=True
        ).update(is_active=False)

        # Create new session
        from django.conf import settings
        expiry = getattr(settings, 'ATTENDX_QR_EXPIRY_SECONDS', 60)
        new_session = QRCodeSession.create_session(active_lecture, expiry)

        # Generate QR image
        qr_url = f"{request.scheme}://{request.get_host()}/attendance/scan/{new_session.token}/"
        qr_img = qrcode.make(qr_url)
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_b64 = base64.b64encode(buffer.getvalue()).decode()

        return JsonResponse({
            'success': True,
            'qr_image_url': f"data:image/png;base64,{qr_b64}",
            'token': new_session.token,
            'expiry_time': new_session.expires_at.isoformat(),
            'lecture_info': {
                'subject': active_lecture.subject.code,
                'section': active_lecture.section.name,
            }
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })
