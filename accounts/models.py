from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractBaseUser):
    class Role(models.TextChoices):
        ADMIN = "admin", _("admin")
        INSTALLER = "installer", _("installer")

    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=255)
    password = models.CharField(_("password"), max_length=128)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    role = models.CharField(_("role"), max_length=30, choices=Role.choices)

    USERNAME_FIELD = "email"

