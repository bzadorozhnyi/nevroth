from django.contrib.auth import get_user_model

from chats.models import Chat

User = get_user_model()


class ChatService:
    @classmethod
    def get_chats_for_user(cls, user: User) -> list[Chat]:
        return Chat.objects.filter(members__user=user).order_by("-created_at")
