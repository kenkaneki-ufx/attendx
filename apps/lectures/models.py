from django.db import models
from django.utils import timezone
from apps.lectures.models_timetable import TimeSlot, Timetable


class Lecture(models.Model):
    """Lecture model for tracking individual lectures."""

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    faculty = models.ForeignKey(
        'accounts.Faculty',
        on_delete=models.RESTRICT,
        related_name='lectures'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.RESTRICT,
        related_name='lectures'
    )
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.RESTRICT,
        related_name='lectures'
    )
    lecture_date = models.DateField(default=timezone.now)
    lecture_number = models.SmallIntegerField()  # 1st, 2nd, 3rd period
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.SmallIntegerField(default=60)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lecture'
        verbose_name_plural = 'Lectures'
        ordering = ['-lecture_date', 'lecture_number']
        unique_together = ['faculty', 'lecture_date', 'lecture_number']

    def __str__(self):
        return f"{self.subject.code} - {self.section} ({self.get_lecture_date_display()})"

    def get_lecture_date_display(self):
        return self.lecture_date.strftime('%b %d, %Y')

    def start(self):
        """Mark lecture as in progress."""
        self.status = 'IN_PROGRESS'
        self.start_time = timezone.now()
        self.save(update_fields=['status', 'start_time', 'updated_at'])

    def end(self):
        """Mark lecture as completed."""
        self.status = 'COMPLETED'
        self.end_time = timezone.now()
        self.save(update_fields=['status', 'end_time', 'updated_at'])

    def cancel(self):
        """Cancel the lecture."""
        self.status = 'CANCELLED'
        self.save(update_fields=['status', 'updated_at'])

    def get_absolute_url(self):
        return f"/lectures/{self.pk}/"
