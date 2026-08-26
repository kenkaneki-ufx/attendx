from django.db import models


class Section(models.Model):
    """Section model for organizing students within a branch."""
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.RESTRICT,
        related_name='sections'
    )
    name = models.CharField(max_length=50)  # e.g., 'Section A', 'Section B'
    semester = models.SmallIntegerField()  # 1-8
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['branch', 'semester', 'name']
        unique_together = ['branch', 'name', 'semester']

    def __str__(self):
        return f"{self.branch.code} - {self.name} (Sem {self.semester})"

    def get_absolute_url(self):
        return f"/sections/{self.pk}/"
