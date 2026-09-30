"""
Signals run code automatically on model events.
Here: create the matching profile row whenever a new User is saved.
Prevents "profile does not exist" bugs — every user always has one.
"""
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StudentProfile, RecruiterProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    instance -> the User that was just saved.
    created  -> True if it was a fresh INSERT, False if an UPDATE.
    """
    # Only on creation. Otherwise profiles would reset on every user save.
    if not created:
        return

    if instance.role == User.Role.STUDENT:
        # get_or_create is defensive: safe even if the profile already exists.
        StudentProfile.objects.get_or_create(user=instance)
    elif instance.role == User.Role.RECRUITER:
        RecruiterProfile.objects.get_or_create(user=instance)