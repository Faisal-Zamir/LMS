from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . models import Course
@receiver(post_save, sender=Course)
@receiver(post_delete, sender=Course)
def update_num_courses(sender, instance, **kwargs):
    """
    Signal receiver function to update the num_courses field of related Category
    whenever a Course object is created or deleted.
    """
    instance.category.update_num_courses()