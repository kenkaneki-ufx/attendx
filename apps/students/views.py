from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, F
from django.core.cache import cache


class StudentPortalView(TemplateView):
    """Public student portal for checking attendance by roll number."""
    template_name = 'students/portal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roll_number = self.request.GET.get('roll_number', '').strip()
        context['roll_number'] = roll_number

        if roll_number:
            ip_address = self.request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f'portal_lookup_{ip_address}'
            lookup_count = cache.get(cache_key, 0)

            if lookup_count >= 10:
                context['error'] = 'Too many requests. Please wait a minute before trying again.'
                return context

            cache.set(cache_key, lookup_count + 1, 60)

            from .models import Student
            from apps.attendance.models import AttendanceRecord

            try:
                student = Student.objects.select_related(
                    'section', 'section__branch', 'section__branch__department'
                ).get(roll_number__iexact=roll_number, is_active=True)
                context['student'] = student

                records = AttendanceRecord.objects.filter(
                    student=student
                ).select_related(
                    'lecture', 'lecture__subject', 'lecture__faculty'
                ).order_by('-lecture__lecture_date')

                total_lectures = records.count()
                present_count = records.filter(status='PRESENT').count()
                late_count = records.filter(status='LATE').count()
                absent_count = records.filter(status='ABSENT').count()

                attendance_rate = (present_count / total_lectures * 100) if total_lectures > 0 else 0

                context['records'] = records
                context['total_lectures'] = total_lectures
                context['present_count'] = present_count
                context['late_count'] = late_count
                context['absent_count'] = absent_count
                context['attendance_rate'] = round(attendance_rate, 1)

            except Student.DoesNotExist:
                context['error'] = f'No active student found with roll number: {roll_number}'

        return context


def student_login_view(request):
    """Student login page using roll number + password."""
    if request.session.get('is_student'):
        return redirect('students:student_dashboard')

    if request.method == 'POST':
        roll_number = request.POST.get('roll_number', '').strip()
        password = request.POST.get('password', '')

        if not roll_number or not password:
            messages.error(request, 'Please enter both roll number and password.')
            return render(request, 'students/login.html')

        from .models import Student
        try:
            student = Student.objects.get(roll_number__iexact=roll_number, is_active=True)
            if student.check_password(password):
                request.session['student_id'] = student.pk
                request.session['student_name'] = student.get_full_name()
                request.session['student_roll'] = student.roll_number
                request.session['is_student'] = True
                messages.success(request, f'Welcome back, {student.first_name}!')
                return redirect('students:student_dashboard')
            else:
                messages.error(request, 'Invalid password. Please try again.')
        except Student.DoesNotExist:
            messages.error(request, f'No active student found with roll number: {roll_number}')

    return render(request, 'students/login.html')


def student_logout_view(request):
    """Logout student and clear session."""
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('students:student_login')


class StudentRequiredMixin:
    """Mixin to ensure only authenticated students can access the view."""
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_student') or not request.session.get('student_id'):
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(f"{reverse('students:student_login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)


class StudentDashboardView(StudentRequiredMixin, TemplateView):
    """Student dashboard showing attendance history and charts."""
    template_name = 'students/dashboard.html'

    def get(self, request, *args, **kwargs):
        from .models import Student
        student_id = request.session.get('student_id')
        try:
            Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            messages.error(request, 'Student not found.')
            return redirect('students:student_login')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')

        from .models import Student
        from apps.attendance.models import AttendanceRecord
        from apps.lectures.models import Lecture

        student = Student.objects.select_related(
            'section', 'section__branch', 'section__branch__department'
        ).get(pk=student_id)
        context['student'] = student

        # Base queryset for all attendance records
        all_records = AttendanceRecord.objects.filter(
            student=student
        ).select_related(
            'lecture', 'lecture__subject', 'lecture__faculty'
        ).order_by('-lecture__lecture_date')

        # Overall stats
        total_lectures = all_records.count()
        present_count = all_records.filter(status='PRESENT').count()
        late_count = all_records.filter(status='LATE').count()
        absent_count = all_records.filter(status='ABSENT').count()

        attendance_rate = (present_count / total_lectures * 100) if total_lectures > 0 else 0

        context['records'] = all_records[:50]
        context['total_lectures'] = total_lectures
        context['present_count'] = present_count
        context['late_count'] = late_count
        context['absent_count'] = absent_count
        context['attendance_rate'] = round(attendance_rate, 1)

        # Subject-wise attendance (aggregation query)
        subject_data = all_records.values(
            subject_name=F('lecture__subject__name'),
            subject_code=F('lecture__subject__code')
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
            late=Count('id', filter=Q(status='LATE')),
            absent=Count('id', filter=Q(status='ABSENT')),
        ).order_by('-total')

        context['subject_data'] = [
            {
                'code': item['subject_code'],
                'name': item['subject_name'],
                'total': item['total'],
                'present': item['present'],
                'late': item['late'],
                'absent': item['absent'],
                'rate': round((item['present'] / item['total'] * 100) if item['total'] > 0 else 0, 1),
            }
            for item in subject_data
        ]

        # Weekly trend (last 7 days) - separate queryset for full data
        today = timezone.now().date()
        week_ago = today - timezone.timedelta(days=6)
        week_map = {}
        for s in AttendanceRecord.objects.filter(
            student=student,
            lecture__lecture_date__gte=week_ago,
            lecture__lecture_date__lte=today,
        ).values('lecture__lecture_date').annotate(
            present=Count('id', filter=Q(status='PRESENT')),
            late=Count('id', filter=Q(status='LATE')),
            absent=Count('id', filter=Q(status='ABSENT')),
        ).order_by('lecture__lecture_date'):
            week_map[str(s['lecture__lecture_date'])] = s

        week_data = []
        for i in range(6, -1, -1):
            day = today - timezone.timedelta(days=i)
            stats = week_map.get(str(day), {'present': 0, 'late': 0, 'absent': 0})
            week_data.append({
                'date': day.strftime('%a'),
                'present': stats['present'],
                'late': stats['late'],
                'absent': stats['absent'],
            })
        context['week_data'] = week_data

        # Monthly trend (last 6 months) - separate queryset
        monthly_data = []
        for i in range(5, -1, -1):
            month_date = today - timezone.timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            if i > 0:
                next_month_start = (month_start + timezone.timedelta(days=32)).replace(day=1)
            else:
                next_month_start = today + timezone.timedelta(days=1)

            month_stats = AttendanceRecord.objects.filter(
                student=student,
                lecture__lecture_date__gte=month_start,
                lecture__lecture_date__lt=next_month_start,
            ).aggregate(
                present=Count('id', filter=Q(status='PRESENT')),
                total=Count('id'),
            )
            rate = (month_stats['present'] / month_stats['total'] * 100) if month_stats['total'] > 0 else 0
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'total': month_stats['total'],
                'present': month_stats['present'],
                'rate': round(rate, 1),
            })
        context['monthly_data'] = monthly_data

        # Recent lectures
        recent_lectures = Lecture.objects.filter(
            section=student.section,
            is_active=True
        ).select_related('subject', 'faculty').order_by('-lecture_date')[:10]
        context['recent_lectures'] = recent_lectures

        return context
