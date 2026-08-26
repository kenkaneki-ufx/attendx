from django.db import models


class ActiveManager(models.Manager):
    """
    Custom manager to return only active records.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteManager(models.Manager):
    """
    Custom manager that includes soft-deleted records.
    """
    def get_queryset(self):
        return super().get_queryset()
