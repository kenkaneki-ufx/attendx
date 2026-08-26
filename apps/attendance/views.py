from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.core.cache import cache
import qrcode
import io
import base64


class LiveAttendanceView(LoginRequiredMixin, TemplateView):
    """View showing live attendance for the current active lecture."""
    template_name = 'attendance/live_attendance.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user

        from apps.lectures.models import Lecture
        from apps.attendance.models import AttendanceRecord

        active_lecture = Lecture.objects.filter(
            faculty=user,
            lecture_date=today,
            status='IN_PROGRESS',
            is_active=True
        ).select_related('subject', 'section').first()

        context['active_lecture'] = active_lecture

        if active_lecture:
            stats = AttendanceRecord.get_attendance_stats(active_lecture)
            context['attendance_stats'] = stats
            context['present_list'] = AttendanceRecord.objects.filter(
                lecture=active_lecture,
                status__in=['PRESENT', 'LATE']
            ).select_related('student').order_by('-scan_time')

            from apps.students.models import Student
            context['total_students'] = Student.objects.filter(
                section=active_lecture.section, is_active=True
            ).count()

        return context


class AttendanceHistoryView(LoginRequiredMixin, TemplateView):
    """View showing attendance history for the faculty."""
    template_name = 'attendance/attendance_list.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        from apps.lectures.models import Lecture
        from apps.attendance.models import AttendanceRecord

        completed_lectures = Lecture.objects.filter(
            faculty=user,
            status='COMPLETED',
            is_active=True
        ).select_related('subject', 'section').order_by('-lecture_date')[:20]

        lecture_data = []
        for lecture in completed_lectures:
            stats = AttendanceRecord.get_attendance_stats(lecture)
            lecture_data.append({
                'lecture': lecture,
                'stats': stats,
            })

        context['lecture_data'] = lecture_data
        return context


def scan_attendance(request, token):
    """View for students to scan QR code and mark attendance."""
    from apps.qr_codes.models import QRCodeSession
    from apps.attendance.models import AttendanceRecord

    # Find the QR session by token
    qr_session = QRCodeSession.objects.filter(
        token=token,
        is_active=True
    ).select_related('lecture', 'lecture__subject', 'lecture__section').first()

    context = {'success': False, 'message': ''}

    if not qr_session:
        context['message'] = 'Invalid QR code. Please ask your faculty for a new one.'
        return render(request, 'attendance/scan_result.html', context)

    if qr_session.is_expired():
        context['message'] = 'QR code has expired. Please ask your faculty to generate a new one.'
        return render(request, 'attendance/scan_result.html', context)

    lecture = qr_session.lecture
    if lecture.status != 'IN_PROGRESS':
        context['message'] = 'This lecture is not currently active.'
        return render(request, 'attendance/scan_result.html', context)

    # Get client info
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    device_info = request.META.get('HTTP_USER_AGENT', '')[:255]

    # Rate limiting: max 10 scans per IP per minute
    rate_limit_key = f'scan_rate_{ip_address}'
    scan_count = cache.get(rate_limit_key, 0)
    if scan_count >= 10:
        context['message'] = 'Too many scan attempts. Please wait a moment and try again.'
        return render(request, 'attendance/scan_result.html', context)
    cache.set(rate_limit_key, scan_count + 1, 60)

    # Check if student is logged in via session
    if not request.session.get('is_student') or not request.session.get('student_id'):
        context['message'] = 'Please login as a student first.'
        return render(request, 'attendance/scan_result.html', context)

    student_id = request.session.get('student_id')

    from apps.students.models import Student
    try:
        student = Student.objects.get(pk=student_id, is_active=True)
    except Student.DoesNotExist:
        context['message'] = 'Student not found.'
        return render(request, 'attendance/scan_result.html', context)

    # Check if student belongs to the lecture's section
    if student.section != lecture.section:
        context['message'] = 'You are not enrolled in this section.'
        return render(request, 'attendance/scan_result.html', context)

    # Mark attendance
    record, created = AttendanceRecord.mark_present(
        student=student,
        lecture=lecture,
        qr_session=qr_session,
        ip_address=ip_address,
        device_info=device_info
    )

    if created:
        context['success'] = True
        context['message'] = f'Attendance marked for {lecture.subject.code} - {lecture.section.name}'
        context['student'] = student
        context['lecture'] = lecture
    else:
        context['message'] = 'You have already submitted attendance for this lecture.'
        context['success'] = True  # Still show success since they're already marked

    return render(request, 'attendance/scan_result.html', context)


@login_required
def attendance_refresh_api(request):
    """AJAX endpoint to refresh attendance list."""
    from apps.lectures.models import Lecture
    from apps.attendance.models import AttendanceRecord
    from django.template.loader import render_to_string

    today = timezone.now().date()
    active_lecture = Lecture.objects.filter(
        faculty=request.user,
        lecture_date=today,
        status='IN_PROGRESS',
        is_active=True
    ).first()

    if not active_lecture:
        return JsonResponse({'success': False, 'message': 'No active lecture'})

    records = AttendanceRecord.objects.filter(
        lecture=active_lecture
    ).select_related('student').order_by('-scan_time')

    stats = AttendanceRecord.get_attendance_stats(active_lecture)
    html = render_to_string('attendance/partials/attendance_list.html', {
        'records': records,
    })

    return JsonResponse({
        'success': True,
        'html': html,
        'present_count': stats['present'],
        'late_count': stats['late'],
        'total_count': stats['total'],
    })
