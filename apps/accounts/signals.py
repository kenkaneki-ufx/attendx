from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

Faculty = get_user_model()


@receiver(post_save, sender=Faculty)
def create_faculty_profile(sender, instance, created, **kwargs):
    """Create profile when faculty is created."""
    if created:
        # Any profile setup logic here
        pass
