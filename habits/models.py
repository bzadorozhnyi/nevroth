from django.db import models
from django.utils.translation import gettext_lazy as _


class Habit(models.Model):
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), max_length=255)
