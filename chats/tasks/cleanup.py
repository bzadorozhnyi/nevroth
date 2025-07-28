from celery import shared_task
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from chats.models import ChatMessage


@shared_task
def cleanup_old_messages_task():
    threshold_date = timezone.now() - timedelta(
        days=settings.OLD_MESSAGE_RETENTION_DAYS
    )

    ChatMessage.objects.filter(created_at__lte=threshold_date).delete()
