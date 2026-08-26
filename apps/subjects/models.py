from django.db import models


class Subject(models.Model):
    """Subject model for academic subjects."""
    code = models.CharField(max_length=20, unique=True)  # e.g., 'CS401'
    name = models.CharField(max_length=200)  # e.g., 'Machine Learning'
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.RESTRICT,
        related_name='subjects'
    )
    semester = models.SmallIntegerField()  # 1-8
    credits = models.SmallIntegerField(default=3)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['department', 'semester', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_absolute_url(self):
        return f"/subjects/{self.pk}/"
