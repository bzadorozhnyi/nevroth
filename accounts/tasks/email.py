from typing import Sequence, Any

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_mail_task(
    subject: str, message: str, recipient_list: Sequence[str], **kwargs: Any
):
    kwargs.setdefault("fail_silently", False)
    send_mail(
        subject=subject,
        message=message,
        recipient_list=recipient_list,
        from_email=settings.DEFAULT_FROM_EMAIL,
        **kwargs,
    )
