"""
Cleanup expired QR code sessions and old attendance records.
Usage: python manage.py cleanup_expired
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Cleanup expired QR sessions and old data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep records (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        self.stdout.write(f'Cleaning up data older than {days} days (before {cutoff_date.date()})...')

        # Cleanup expired QR sessions
        from apps.qr_codes.models import QRCodeSession
        expired_qr = QRCodeSession.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        qr_count = expired_qr.count()
        if not dry_run:
            expired_qr.update(is_active=False)
        self.stdout.write(f'  Deactivated {qr_count} expired QR sessions')

        # Cleanup old inactive QR sessions
        old_qr = QRCodeSession.objects.filter(
            created_at__lt=cutoff_date,
            is_active=False
        )
        old_qr_count = old_qr.count()
        if not dry_run:
            old_qr.delete()
        self.stdout.write(f'  Deleted {old_qr_count} old inactive QR sessions')

        # Cleanup old completed lectures and their attendance
        from apps.lectures.models import Lecture
        from apps.attendance.models import AttendanceRecord

        old_lectures = Lecture.objects.filter(
            lecture_date__lt=cutoff_date.date(),
            status__in=['COMPLETED', 'CANCELLED']
        )
        old_lecture_count = old_lectures.count()

        if not dry_run:
            # Delete attendance records for old lectures first
            AttendanceRecord.objects.filter(
                lecture__in=old_lectures
            ).delete()
            old_lectures.delete()

        self.stdout.write(f'  Deleted {old_lecture_count} old lectures and their attendance records')

        self.stdout.write(self.style.SUCCESS('Cleanup complete!'))
