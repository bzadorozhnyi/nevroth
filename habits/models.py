from django.db import models
from django.utils.translation import gettext_lazy as _

from django.conf import settings


class Habit(models.Model):
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), max_length=255)


class UserHabit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "habit")
