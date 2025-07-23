from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

from chats.models import Chat, ChatMember

User = get_user_model()


class ChatService:
    @classmethod
    def get_user_chats(cls, user: User) -> list[Chat]:
        return Chat.objects.filter(members__user=user).order_by("-created_at")

    @classmethod
    def get_chat_between(cls, user1: User, user2_id: int) -> Chat:
        return (
            Chat.objects.filter(chat_type=Chat.ChatType.PRIVATE)
            .filter(members__user=user1)
            .filter(members__user__id=user2_id)
            .distinct()
            .first()
        )

    @classmethod
    @transaction.atomic
    def create_chat_between(cls, user1: User, user2_id: int) -> Chat:
        chat = Chat.objects.create(chat_type=Chat.ChatType.PRIVATE)
        ChatMember.objects.bulk_create(
            [ChatMember(chat=chat, user=user1), ChatMember(chat=chat, user_id=user2_id)]
        )

        return chat

    @classmethod
    def get_or_create_chat_between(cls, user1: User, user2_id: int) -> Chat:
        if user1.id == user2_id:
            raise ValidationError(_("You can't create chat with yourself!"))

        existing_chat = cls.get_chat_between(user1, user2_id)
        if existing_chat:
            return existing_chat

        return cls.create_chat_between(user1, user2_id)

    @classmethod
    def is_user_in_chat(cls, user: User, chat_id: int) -> bool:
        return ChatMember.objects.filter(chat_id=chat_id, user=user).exists()

    @classmethod
    def get_chat_members_ids(cls, chat: Chat) -> list[int]:
        return ChatMember.objects.filter(chat=chat).values_list("user", flat=True)
