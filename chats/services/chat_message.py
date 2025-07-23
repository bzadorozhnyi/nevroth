from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chats.consumers.groups import WebSocketGroup
from chats.enums import ChatWebSocketServerEventType
from chats.models import Chat, ChatMessage
from chats.services.chat import ChatService

from django.contrib.auth import get_user_model

User = get_user_model()


class ChatMessageService:
    @classmethod
    def create_message(cls, sender: User, chat: Chat, content: str) -> ChatMessage:
        return ChatMessage.objects.create(sender=sender, chat=chat, content=content)

    @classmethod
    def notify_new_message(cls, chat_message: ChatMessage):
        from chats.serializers import (
            ChatMessageForWebsocketSerializer,
            NewMessageForWebsocketSerializer,
        )

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            WebSocketGroup.chat(chat_message.chat.id),
            {
                "type": ChatWebSocketServerEventType.NEW_MESSAGE,
                "message": ChatMessageForWebsocketSerializer(chat_message).data,
            },
        )

        members_ids = ChatService.get_chat_members_ids(chat_message.chat)
        new_message = NewMessageForWebsocketSerializer(chat_message).data
        for member_id in members_ids:
            if member_id == chat_message.sender.id:
                continue

            async_to_sync(channel_layer.group_send)(
                WebSocketGroup.chat_list(member_id),
                {
                    "type": ChatWebSocketServerEventType.NEW_MESSAGE,
                    "message": new_message,
                },
            )
