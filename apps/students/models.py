from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Student(models.Model):
    """Student model for managing student records."""
    registration_number = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    password_hash = models.CharField(max_length=128, blank=True, null=True, help_text='Hashed password for student login')
    section = models.ForeignKey(
        'sections.Section',
        on_delete=models.RESTRICT,
        related_name='students'
    )
    admission_year = models.SmallIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['section', 'roll_number']
        unique_together = ['roll_number', 'section']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, raw_password):
        """Set the password for the student."""
        self.password_hash = make_password(raw_password)
        self.save(update_fields=['password_hash'])

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
        if not self.password_hash:
            return False
        return check_password(raw_password, self.password_hash)

    def get_absolute_url(self):
        return f"/students/{self.pk}/"
