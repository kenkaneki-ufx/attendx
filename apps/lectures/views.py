from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from .models import Lecture


class StartLectureView(LoginRequiredMixin, TemplateView):
    """View to start a new lecture."""
    template_name = 'lectures/start_lecture.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from apps.faculty.models import FacultySubjectAssignment
        context['assignments'] = FacultySubjectAssignment.objects.filter(
            faculty=user, is_active=True
        ).select_related('subject', 'section')
        return context

    def post(self, request, *args, **kwargs):
        from django.utils import timezone as tz
        from apps.subjects.models import Subject
        from apps.sections.models import Section

        subject_id = request.POST.get('subject_id')
        section_id = request.POST.get('section_id')
        lecture_number = request.POST.get('lecture_number', 1)
        duration = request.POST.get('duration_minutes', 60)

        subject = get_object_or_404(Subject, pk=subject_id)
        section = get_object_or_404(Section, pk=section_id)
        now = tz.now()

        lecture = Lecture.objects.create(
            faculty=request.user,
            subject=subject,
            section=section,
            lecture_date=now.date(),
            lecture_number=int(lecture_number),
            start_time=now,
            end_time=now + tz.timedelta(minutes=int(duration)),
            duration_minutes=int(duration),
            status='IN_PROGRESS'
        )

        messages.success(request, f'Lecture started: {subject.code} - {section.name}')
        return redirect('lectures:active_lecture', pk=lecture.pk)


class ActiveLectureView(LoginRequiredMixin, TemplateView):
    """View showing the currently active lecture with QR code."""
    template_name = 'lectures/active_lecture.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        lecture = get_object_or_404(Lecture, pk=pk, faculty=self.request.user)
        context['lecture'] = lecture

        from apps.attendance.models import AttendanceRecord
        stats = AttendanceRecord.get_attendance_stats(lecture)
        context['attendance_stats'] = stats

        from apps.students.models import Student
        context['total_students'] = Student.objects.filter(
            section=lecture.section, is_active=True
        ).count()

        # Check for active QR session
        from apps.qr_codes.models import QRCodeSession
        active_qr = QRCodeSession.objects.filter(
            lecture=lecture, is_active=True
        ).first()
        context['active_qr'] = active_qr

        # Generate QR image
        if active_qr:
            import qrcode
            import io
            import base64
            qr_url = f"{self.request.scheme}://{self.request.get_host()}/attendance/scan/{active_qr.token}/"
            qr_img = qrcode.make(qr_url)
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            context['qr_image'] = base64.b64encode(buffer.getvalue()).decode()
            remaining = (active_qr.expires_at - timezone.now()).total_seconds()
            context['remaining_seconds'] = max(0, int(remaining))
            context['expiry_time'] = active_qr.expires_at.isoformat()

        return context


class EndLectureView(LoginRequiredMixin, TemplateView):
    """View to end an active lecture and mark absent students."""
    template_name = 'lectures/active_lecture.html'
    login_url = '/accounts/login/'

    def post(self, request, pk, *args, **kwargs):
        lecture = get_object_or_404(Lecture, pk=pk, faculty=request.user, status='IN_PROGRESS')

        # Mark absent students
        from apps.students.models import Student
        from apps.attendance.models import AttendanceRecord
        from apps.qr_codes.models import QRCodeSession

        # Get students in the section
        section_students = Student.objects.filter(section=lecture.section, is_active=True)

        # Get students who already have attendance records
        present_student_ids = AttendanceRecord.objects.filter(
            lecture=lecture
        ).values_list('student_id', flat=True)

        # Mark absent students
        qr_session = QRCodeSession.objects.filter(lecture=lecture).first()
        if qr_session:
            for student in section_students:
                if student.pk not in present_student_ids:
                    AttendanceRecord.objects.create(
                        student=student,
                        lecture=lecture,
                        qr_session=qr_session,
                        status='ABSENT'
                    )

        # Deactivate all QR sessions for this lecture
        QRCodeSession.objects.filter(lecture=lecture).update(is_active=False)

        # End the lecture
        lecture.end()

        messages.success(request, f'Lecture ended: {lecture.subject.code} - {lecture.section.name}')
        return redirect('lectures:lecture_list')


class LectureListView(LoginRequiredMixin, ListView):
    """View listing all lectures for the faculty."""
    model = Lecture
    template_name = 'lectures/lecture_list.html'
    context_object_name = 'lectures'
    login_url = '/accounts/login/'
    paginate_by = 20

    def get_queryset(self):
        return Lecture.objects.filter(
            faculty=self.request.user
        ).select_related('subject', 'section')
