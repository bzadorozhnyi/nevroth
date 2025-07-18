from django.contrib.auth import get_user_model


from chats.models import Chat, ChatMessage

User = get_user_model()


class ChatMessageService:
    @classmethod
    def create_message(cls, sender: User, chat: Chat, content: str) -> ChatMessage:
        return ChatMessage.objects.create(sender=sender, chat=chat, content=content)
