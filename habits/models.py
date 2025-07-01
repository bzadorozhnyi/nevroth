from django.db import models
from django.utils.translation import gettext_lazy as _

from django.conf import settings


class Habit(models.Model):
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), max_length=255)

    def __str__(self):
        return f"{self.name} – {self.description[:30]}..."


class UserHabit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "habit")


class HabitProgress(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", _("success")
        FAIL = "fail", _("fail")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user"))
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, verbose_name=_("habit"))
    date = models.DateField(_("date"), auto_now_add=True)

    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    status = models.CharField(_("status"), max_length=10, choices=Status.choices)

    class Meta:
        unique_together = ("user", "habit", "date")

    def __str__(self):
        return f"{self.user} - {self.habit} on {self.date}: {self.status}"
