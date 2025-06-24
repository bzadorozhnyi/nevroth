import uuid

from django.core.mail import send_mail
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager
from nevroth import settings


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

    is_superuser = models.BooleanField(_("superuser"), default=False)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site.")
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

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

        send_mail(
            subject=subject,
            message=plain_text,
            recipient_list=[self.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
        )
