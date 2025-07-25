import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager
from django.conf import settings

from accounts.tasks import send_mail_task
from habits.models import Habit


class User(AbstractBaseUser):
    class Role(models.TextChoices):
        ADMIN = "admin", _("admin")
        MEMBER = "member", _("member")

    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=255)
    password = models.CharField(_("password"), max_length=128)
    habits = models.ManyToManyField(
        Habit, through="habits.UserHabit", verbose_name=_("habits")
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    role = models.CharField(_("role"), max_length=30, choices=Role.choices)

    is_superuser = models.BooleanField(_("superuser"), default=False)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        indexes = [
            models.Index(fields=["full_name"]),
        ]

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class VerifyToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(_("email address"))
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def save(self, *args, **kwargs):
        creating = True if not self.pk else False
        if creating:
            VerifyToken.objects.filter(email=self.email).delete()

        super().save(*args, **kwargs)

    @property
    def restore_link(self):
        base_domain = settings.BASE_UI_DOMAIN
        protocol = settings.UI_URL_PROTOCOL

        return f"{protocol}{base_domain}/password/reset/{self.token}"

    def send_email_to_restore_password(self):
        subject = _("Nevroth Restore Password")
        plain_text = f"Restore password link: {self.restore_link}"

        send_mail_task.delay(
            subject,
            plain_text,
            [self.email],
        )
