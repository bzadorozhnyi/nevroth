from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver

from habits.models import Habit


@receiver([post_save, post_delete], sender=Habit)
def invalidate_habit_cache(sender, instance, **kwargs):
    cache.delete_pattern("*habits-list*")
