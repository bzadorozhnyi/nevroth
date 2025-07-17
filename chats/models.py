from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Chat(models.Model):
    class ChatType(models.TextChoices):
        PRIVATE = "private", _("private")
        GROUP = "group", _("group")

    chat_type = models.CharField(
        _("chat_type"), max_length=16, choices=ChatType.choices
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return f"Chat {self.id} ({self.chat_type})"


class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("chat", "user")

    def __str__(self):
        return f"{self.user.full_name} in Chat {self.chat.id}"


class ChatMessage(models.Model):
    content = models.CharField(_("content"), max_length=256, blank=False)
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name="messages", verbose_name=_("chat")
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name=_("sender"),
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return f"[Chat {self.chat_id}] {self.content[:30]}... by {self.sender.full_name} ({self.created_at:%Y-%m-%d %H:%M})"
