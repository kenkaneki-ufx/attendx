from django.db import models


class Branch(models.Model):
    """Branch model for academic branches within a department."""
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.RESTRICT,
        related_name='branches'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ['department', 'name']
        unique_together = ['department', 'code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_absolute_url(self):
        return f"/branches/{self.pk}/"
