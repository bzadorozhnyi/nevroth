from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import PermissionDenied

from chats.models import Chat, ChatMessage
from chats.services.chat import ChatService

User = get_user_model()


class ChatMessageService:
    @classmethod
    def create_message(cls, sender: User, chat: Chat, content: str) -> ChatMessage:
        if not ChatService.is_member_of_chat(sender, chat):
            raise PermissionDenied(_("User is not a member of this chat"))

        return ChatMessage.objects.create(sender=sender, chat=chat, content=content)
