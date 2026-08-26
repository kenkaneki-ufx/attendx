from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Q


class FacultyDashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard showing today's overview for faculty."""
    template_name = 'dashboard/faculty_dashboard.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user

        # Import models here to avoid circular imports
        from apps.lectures.models import Lecture
        from apps.attendance.models import AttendanceRecord

        # Today's lectures
        todays_lectures = Lecture.objects.filter(
            faculty=user,
            lecture_date=today,
            is_active=True
        ).select_related('subject', 'section')

        active_lecture = todays_lectures.filter(status='IN_PROGRESS').first()

        # Attendance stats for today
        today_attendance = AttendanceRecord.objects.filter(
            lecture__faculty=user,
            lecture__lecture_date=today
        )
        present_count = today_attendance.filter(status='PRESENT').count()
        late_count = today_attendance.filter(status='LATE').count()

        # Total students across today's sections
        section_ids = todays_lectures.values_list('section_id', flat=True).distinct()
        from apps.students.models import Student
        total_students = Student.objects.filter(
            section_id__in=section_ids,
            is_active=True
        ).count()

        # This week's attendance rate
        week_start = today - timezone.timedelta(days=today.weekday())
        week_attendance = AttendanceRecord.objects.filter(
            lecture__faculty=user,
            lecture__lecture_date__gte=week_start,
            lecture__lecture_date__lte=today
        )
        week_present = week_attendance.filter(status='PRESENT').count()
        week_total = week_attendance.count()
        week_rate = (week_present / week_total * 100) if week_total > 0 else 0

        context.update({
            'todays_lectures': todays_lectures,
            'active_lecture': active_lecture,
            'present_count': present_count,
            'late_count': late_count,
            'total_students': total_students,
            'today': today,
            'week_rate': round(week_rate, 1),
            'total_lectures_today': todays_lectures.count(),
        })
        return context
