from django.db import models


class FacultySubjectAssignment(models.Model):
    """Maps faculty members to subjects and sections for an academic year."""
    faculty = models.ForeignKey(
        'accounts.Faculty',
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='faculty_assignments'
    )
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.CASCADE,
        related_name='faculty_assignments'
    )
    academic_year = models.CharField(max_length=9)  # e.g., '2025-2026'
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Faculty Subject Assignment'
        verbose_name_plural = 'Faculty Subject Assignments'
        unique_together = ['faculty', 'subject', 'section', 'academic_year']
        ordering = ['-academic_year', 'faculty', 'subject']

    def __str__(self):
        return f"{self.faculty} -> {self.subject} ({self.section}) [{self.academic_year}]"
