from typing import Any
from celery import shared_task

from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from accounts.services.user import UserService

User = get_user_model()


@shared_task(
    max_retries=2,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def follow_up_no_habits_selected_task(user_id: int, **kwargs: Any):
    if UserService.has_selected_habits(user_id):
        return

    user = User.objects.get(id=user_id)
    subject = _("Nevroth Select Habits Reminder")
    html_message = render_to_string("accounts/select_habits_reminder.html")

    send_mail(
        subject=subject,
        message=html_message,
        recipient_list=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        **kwargs,
    )
