from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
import csv
from io import StringIO


class DailyReportView(LoginRequiredMixin, TemplateView):
    """View for daily attendance report."""
    template_name = 'reports/daily_report.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user

        from apps.lectures.models import Lecture
        from apps.attendance.models import AttendanceRecord

        lectures = Lecture.objects.filter(
            faculty=user,
            lecture_date=today,
            is_active=True
        ).select_related('subject', 'section')

        report_data = []
        for lecture in lectures:
            stats = AttendanceRecord.get_attendance_stats(lecture)
            report_data.append({'lecture': lecture, 'stats': stats})

        context['report_data'] = report_data
        context['report_date'] = today
        return context


class WeeklyReportView(LoginRequiredMixin, TemplateView):
    """View for weekly attendance report."""
    template_name = 'reports/weekly_report.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())
        user = self.request.user

        from apps.attendance.models import AttendanceRecord

        week_stats = []
        for i in range(7):
            day = week_start + timezone.timedelta(days=i)
            count = AttendanceRecord.objects.filter(
                lecture__faculty=user,
                lecture__lecture_date=day,
                status='PRESENT'
            ).count()
            week_stats.append({'date': day, 'present_count': count})

        context['week_stats'] = week_stats
        context['week_start'] = week_start
        context['week_end'] = week_start + timezone.timedelta(days=6)
        return context


class MonthlyReportView(LoginRequiredMixin, TemplateView):
    """View for monthly attendance report."""
    template_name = 'reports/monthly_report.html'
    login_url = '/accounts/login/'


@login_required
def export_daily_csv(request):
    """Export daily attendance report as CSV."""
    from apps.lectures.models import Lecture
    from apps.attendance.models import AttendanceRecord

    today = timezone.now().date()
    user = request.user

    lectures = Lecture.objects.filter(
        faculty=user,
        lecture_date=today,
        is_active=True
    ).select_related('subject', 'section')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_daily_{today}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Subject', 'Section', 'Period', 'Present', 'Late', 'Absent', 'Rate %'])

    for lecture in lectures:
        stats = AttendanceRecord.get_attendance_stats(lecture)
        writer.writerow([
            today.strftime('%Y-%m-%d'),
            f'{lecture.subject.code} - {lecture.subject.name}',
            lecture.section.name,
            lecture.lecture_number,
            stats['present'],
            stats['late'],
            stats['absent'],
            f"{stats['attendance_rate']:.1f}",
        ])

    return response


@login_required
def export_attendance_csv(request):
    """Export detailed attendance records as CSV."""
    from apps.attendance.models import AttendanceRecord

    user = request.user
    records = AttendanceRecord.objects.filter(
        lecture__faculty=user
    ).select_related(
        'student', 'lecture', 'lecture__subject', 'lecture__section'
    ).order_by('-lecture__lecture_date')[:500]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_records.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Subject', 'Section', 'Student', 'Roll Number', 'Status', 'Scan Time'])

    for record in records:
        writer.writerow([
            record.lecture.lecture_date.strftime('%Y-%m-%d'),
            record.lecture.subject.code,
            record.lecture.section.name,
            record.student.get_full_name(),
            record.student.roll_number,
            record.status,
            record.scan_time.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


@login_required
def export_daily_pdf(request):
    """Export daily attendance report as PDF."""
    from apps.lectures.models import Lecture
    from apps.attendance.models import AttendanceRecord
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch

    today = timezone.now().date()
    user = request.user

    lectures = Lecture.objects.filter(
        faculty=user,
        lecture_date=today,
        is_active=True
    ).select_related('subject', 'section')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_daily_{today}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f'Daily Attendance Report - {today.strftime("%B %d, %Y")}', styles['Title']))
    elements.append(Spacer(1, 0.5 * inch))

    # Data
    data = [['Subject', 'Section', 'Period', 'Present', 'Late', 'Absent', 'Rate %']]
    for lecture in lectures:
        stats = AttendanceRecord.get_attendance_stats(lecture)
        data.append([
            f'{lecture.subject.code}',
            lecture.section.name,
            str(lecture.lecture_number),
            str(stats['present']),
            str(stats['late']),
            str(stats['absent']),
            f"{stats['attendance_rate']:.1f}%",
        ])

    if len(data) > 1:
        table = Table(data, colWidths=[1.2*inch, 1*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph('No lectures found for today.', styles['Normal']))

    doc.build(elements)
    return response
