from django.db import models


class Habit(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
