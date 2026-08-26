from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Q, F


class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    """Enhanced analytics dashboard with multiple chart views."""
    template_name = 'analytics/dashboard.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user

        from apps.attendance.models import AttendanceRecord
        from apps.students.models import Student

        # Overall stats
        total_records = AttendanceRecord.objects.filter(lecture__faculty=user)
        context['total_present'] = total_records.filter(status='PRESENT').count()
        context['total_late'] = total_records.filter(status='LATE').count()
        context['total_absent'] = total_records.filter(status='ABSENT').count()
        context['total_lectures'] = total_records.values('lecture').distinct().count()

        # Attendance rate
        total_count = total_records.count()
        present_count = context['total_present']
        context['attendance_rate'] = round((present_count / total_count * 100) if total_count > 0 else 0, 1)

        # Recent 7 days trend - single query with date trunc
        from django.db.models.functions import TruncDate
        week_ago = today - timezone.timedelta(days=6)
        week_stats = AttendanceRecord.objects.filter(
            lecture__faculty=user,
            lecture__lecture_date__gte=week_ago,
            lecture__lecture_date__lte=today,
        ).values('lecture__lecture_date').annotate(
            present=Count('id', filter=Q(status='PRESENT')),
            late=Count('id', filter=Q(status='LATE')),
            absent=Count('id', filter=Q(status='ABSENT')),
        ).order_by('lecture__lecture_date')

        week_map = {str(s['lecture__lecture_date']): s for s in week_stats}
        week_data = []
        for i in range(6, -1, -1):
            day = today - timezone.timedelta(days=i)
            day_str = str(day)
            stats = week_map.get(day_str, {'present': 0, 'late': 0, 'absent': 0})
            week_data.append({
                'date': day.strftime('%a'),
                'present': stats['present'],
                'late': stats['late'],
                'absent': stats['absent'],
            })
        context['week_data'] = week_data

        # Subject-wise attendance
        subject_data = AttendanceRecord.objects.filter(
            lecture__faculty=user
        ).values(
            subject_name=F('lecture__subject__name'),
            subject_code=F('lecture__subject__code')
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
            late=Count('id', filter=Q(status='LATE')),
        ).order_by('-total')[:8]

        subject_stats = [
            {
                'name': item['subject_code'],
                'full_name': item['subject_name'],
                'total': item['total'],
                'present': item['present'],
                'late': item['late'],
                'rate': round((item['present'] / item['total'] * 100) if item['total'] > 0 else 0, 1),
            }
            for item in subject_data
        ]
        context['subject_data'] = subject_stats

        # Section-wise attendance
        section_data = AttendanceRecord.objects.filter(
            lecture__faculty=user
        ).values(
            section_name=F('lecture__section__name'),
            branch_name=F('lecture__section__branch__name')
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
        ).order_by('-total')[:6]

        context['section_data'] = [
            {
                'name': item['section_name'],
                'branch': item['branch_name'],
                'total': item['total'],
                'present': item['present'],
                'rate': round((item['present'] / item['total'] * 100) if item['total'] > 0 else 0, 1),
            }
            for item in section_data
        ]

        # Monthly trend (last 6 months) - optimized
        monthly_data = []
        for i in range(5, -1, -1):
            month_date = today - timezone.timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            if i > 0:
                next_month_start = (month_start + timezone.timedelta(days=32)).replace(day=1)
            else:
                next_month_start = today + timezone.timedelta(days=1)

            stats = AttendanceRecord.objects.filter(
                lecture__faculty=user,
                lecture__lecture_date__gte=month_start,
                lecture__lecture_date__lt=next_month_start,
            ).aggregate(
                present=Count('id', filter=Q(status='PRESENT')),
                total=Count('id'),
            )

            rate = (stats['present'] / stats['total'] * 100) if stats['total'] > 0 else 0
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'present': stats['present'],
                'total': stats['total'],
                'rate': round(rate, 1),
            })
        context['monthly_data'] = monthly_data

        # Top students by attendance - single aggregation query
        top_students = AttendanceRecord.objects.filter(
            lecture__faculty=user,
            status='PRESENT'
        ).values(
            'student__roll_number',
            'student__first_name',
            'student__last_name',
        ).annotate(
            present_count=Count('id')
        ).order_by('-present_count')[:10]

        context['top_students'] = [
            {
                'roll_number': s['student__roll_number'],
                'name': f"{s['student__first_name']} {s['student__last_name']}",
                'present_count': s['present_count'],
            }
            for s in top_students
        ]

        # Low attendance students - optimized with single aggregation query
        low_attendance = AttendanceRecord.objects.filter(
            lecture__faculty=user,
            student__is_active=True,
        ).values(
            'student__roll_number',
            'student__first_name',
            'student__last_name',
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
        ).filter(
            total__gte=3,
        ).order_by('present')[:20]

        context['low_attendance_students'] = [
            {
                'roll_number': s['student__roll_number'],
                'name': f"{s['student__first_name']} {s['student__last_name']}",
                'total': s['total'],
                'present': s['present'],
                'rate': round((s['present'] / s['total'] * 100), 1),
            }
            for s in low_attendance
            if (s['present'] / s['total'] * 100) < 75
        ][:10]

        return context


class SubjectAnalyticsView(LoginRequiredMixin, TemplateView):
    """Detailed analytics for a specific subject."""
    template_name = 'analytics/subject_analytics.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs.get('subject_id')
        user = self.request.user

        from apps.attendance.models import AttendanceRecord
        from apps.subjects.models import Subject

        subject = get_object_or_404(Subject, pk=subject_id)
        context['subject'] = subject

        # Attendance by section for this subject
        section_data = AttendanceRecord.objects.filter(
            lecture__faculty=user,
            lecture__subject=subject
        ).values(
            section_name=F('lecture__section__name'),
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
        ).order_by('-total')

        context['section_data'] = [
            {
                'name': item['section_name'],
                'total': item['total'],
                'present': item['present'],
                'rate': round((item['present'] / item['total'] * 100) if item['total'] > 0 else 0, 1),
            }
            for item in section_data
        ]

        # Daily trend for this subject - single aggregation query
        today = timezone.now().date()
        fourteen_days_ago = today - timezone.timedelta(days=13)
        daily_stats = AttendanceRecord.objects.filter(
            lecture__faculty=user,
            lecture__subject=subject,
            lecture__lecture_date__gte=fourteen_days_ago,
            lecture__lecture_date__lte=today,
            status='PRESENT'
        ).values('lecture__lecture_date').annotate(
            count=Count('id')
        ).order_by('lecture__lecture_date')

        daily_map = {str(s['lecture__lecture_date']): s['count'] for s in daily_stats}
        daily_data = []
        for i in range(13, -1, -1):
            day = today - timezone.timedelta(days=i)
            daily_data.append({
                'date': day.strftime('%b %d'),
                'count': daily_map.get(str(day), 0),
            })
        context['daily_data'] = daily_data

        return context
