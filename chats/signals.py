from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from chats.models import ChatMessage
from chats.services.chat_message import ChatMessageService


@receiver([post_save], sender=ChatMessage)
def notify_new_message(sender, instance, created, **kwargs):
    if created:
        ChatMessageService.notify_about_new_message(instance)
