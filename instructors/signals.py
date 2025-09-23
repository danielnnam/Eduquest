# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# from .models import InstructorProfile

# User = get_user_model()

# @receiver(post_save, sender=User)
# def create_instructor_profile(sender, instance, created, **kwargs):
#     if created and hasattr(instance, 'is_instructor') and instance.is_instructor:
#         InstructorProfile.objects.create(user=instance)
