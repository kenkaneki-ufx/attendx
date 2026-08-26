"""
Check student attendance and send alerts for low attendance.
Usage: python manage.py check_low_attendance
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Check student attendance and send alerts for low attendance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=float,
            default=75.0,
            help='Attendance threshold percentage (default: 75)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails'
        )

    def handle(self, *args, **options):
        threshold = options['threshold']
        dry_run = options['dry_run']

        self.stdout.write(f'Checking attendance below {threshold}%...')

        from apps.students.models import Student
        from apps.attendance.models import AttendanceRecord

        # Get all active students
        students = Student.objects.filter(is_active=True).select_related(
            'section', 'section__branch', 'section__branch__department'
        )

        alerts_sent = 0

        for student in students:
            # Get attendance records for this student
            records = AttendanceRecord.objects.filter(student=student)
            total = records.count()

            if total == 0:
                continue

            present = records.filter(status='PRESENT').count()
            rate = (present / total) * 100

            if rate < threshold:
                subject = f'Low Attendance Alert - {rate:.1f}%'
                message = (
                    f'Dear {student.get_full_name()},\n\n'
                    f'Your current attendance is {rate:.1f}% which is below the required {threshold}%.\n\n'
                    f'Attendance Summary:\n'
                    f'- Total Lectures: {total}\n'
                    f'- Present: {present}\n'
                    f'- Attendance Rate: {rate:.1f}%\n\n'
                    f'Please attend all upcoming classes to avoid being marked absent.\n\n'
                    f'Regards,\n'
                    f'AttendX Team'
                )

                if dry_run:
                    self.stdout.write(f'  [DRY RUN] Would send email to: {student.email or "No email"} ({student.get_full_name()} - {rate:.1f}%)')
                else:
                    if student.email:
                        try:
                            send_mail(
                                subject=subject,
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[student.email],
                                fail_silently=True,
                            )
                            alerts_sent += 1
                            self.stdout.write(f'  Sent alert to: {student.email} ({student.get_full_name()} - {rate:.1f}%)')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'  Failed to send to {student.email}: {e}'))
                    else:
                        self.stdout.write(f'  Skipped {student.get_full_name()} - no email address')

        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN - No emails sent. Would have sent {alerts_sent} alerts.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Sent {alerts_sent} low attendance alerts.'))
