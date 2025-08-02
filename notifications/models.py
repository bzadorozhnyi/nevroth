from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _


class NotificationMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("sender")
    )
    image_path = models.CharField(
        max_length=1024, null=True, blank=True, verbose_name=_("S3 File Path")
    )
    text = models.TextField(_("text"), max_length=300)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    @property
    def image_url(self) -> str | None:
        if self.image_path:
            return default_storage.url(self.image_path)
        return None


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("recipient"),
    )
    message = models.ForeignKey(
        NotificationMessage,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("message"),
    )
    is_read = models.BooleanField(_("is read"), default=False)
    sent_at = models.DateTimeField(_("sent at"), auto_now_add=True)
