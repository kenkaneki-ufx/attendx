from django.db import models


class TimeSlot(models.Model):
    """Time slot model for lecture periods."""
    slot_number = models.SmallIntegerField(unique=True)  # 1, 2, 3, etc.
    start_time = models.TimeField()  # 09:10
    end_time = models.TimeField()    # 10:10
    label = models.CharField(max_length=50)  # "09:10 AM - 10:10 AM"

    class Meta:
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        ordering = ['slot_number']

    def __str__(self):
        return self.label


class Timetable(models.Model):
    """Timetable model for weekly recurring class schedules."""

    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    LECTURE_TYPE_CHOICES = [
        ('LECTURE', 'Lecture'),
        ('LAB', 'Lab'),
        ('TUTORIAL', 'Tutorial'),
        ('LUNCH', 'Lunch Break'),
    ]

    day_of_week = models.SmallIntegerField(choices=DAY_CHOICES)
    time_slot = models.ForeignKey(
        'lectures.TimeSlot',
        on_delete=models.RESTRICT,
        related_name='timetable_entries'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.RESTRICT,
        related_name='timetable_entries',
        null=True,
        blank=True
    )
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.RESTRICT,
        related_name='timetable_entries'
    )
    faculty = models.ForeignKey(
        'accounts.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_entries'
    )
    lecture_type = models.CharField(
        max_length=20,
        choices=LECTURE_TYPE_CHOICES,
        default='LECTURE'
    )
    room = models.CharField(max_length=50, blank=True, null=True)  # e.g., "FLOOR-1/A-201"
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Timetable Entry'
        verbose_name_plural = 'Timetable Entries'
        ordering = ['day_of_week', 'time_slot__slot_number']
        unique_together = ['day_of_week', 'time_slot', 'section']

    def __str__(self):
        day_name = self.get_day_of_week_display()
        return f"{day_name} {self.time_slot} - {self.subject.code if self.subject else 'N/A'} ({self.section})"

    def get_day_name(self):
        return self.get_day_of_week_display()
