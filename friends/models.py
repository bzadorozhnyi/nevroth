from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class FriendsRelation(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "accepted", _("accepted")
        REJECTED = "rejected", _("rejected")
        PENDING = "pending", _("pending")

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
        verbose_name=_("from user"),
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
        verbose_name=_("to user"),
    )

    status = models.CharField(
        _("status"), max_length=8, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")
        indexes = [
            models.Index(fields=["from_user"]),
            models.Index(fields=["to_user"]),
            models.Index(fields=["status"]),
        ]
