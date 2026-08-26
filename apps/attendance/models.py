from django.db import models
from django.utils import timezone


class AttendanceRecord(models.Model):
    """Attendance Record model for tracking student attendance."""

    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.RESTRICT,
        related_name='attendance_records'
    )
    lecture = models.ForeignKey(
        'lectures.Lecture',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    qr_session = models.ForeignKey(
        'qr_codes.QRCodeSession',
        on_delete=models.RESTRICT,
        related_name='attendance_records'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PRESENT'
    )
    scan_time = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        ordering = ['-scan_time']
        unique_together = ['student', 'lecture']

    def __str__(self):
        return f"{self.student} - {self.lecture} ({self.status})"

    def verify(self):
        """Verify the attendance record."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'verified_at'])

    def mark_late(self):
        """Mark attendance as late."""
        self.status = 'LATE'
        self.save(update_fields=['status'])

    @classmethod
    def mark_present(cls, student, lecture, qr_session, ip_address=None, device_info=None):
        """Mark a student as present for a lecture."""
        record, created = cls.objects.get_or_create(
            student=student,
            lecture=lecture,
            defaults={
                'qr_session': qr_session,
                'status': 'PRESENT',
                'ip_address': ip_address,
                'device_info': device_info,
            }
        )
        return record, created

    @classmethod
    def get_attendance_stats(cls, lecture):
        """Get attendance statistics for a lecture."""
        total = cls.objects.filter(lecture=lecture).count()
        present = cls.objects.filter(lecture=lecture, status='PRESENT').count()
        late = cls.objects.filter(lecture=lecture, status='LATE').count()
        absent = cls.objects.filter(lecture=lecture, status='ABSENT').count()

        return {
            'total': total,
            'present': present,
            'late': late,
            'absent': absent,
            'attendance_rate': (present / total * 100) if total > 0 else 0,
        }

    def get_absolute_url(self):
        return f"/attendance/record/{self.pk}/"
