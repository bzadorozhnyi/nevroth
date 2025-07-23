from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from accounts.serializers import UserWebSocketSerializer
from chats.enums import (
    ChatWebSocketCloseCode,
    ChatWebSocketClientEventType,
    ChatWebSocketServerEventType,
)
from chats.services.chat import ChatService
from chats.consumers.groups import chat_group_name, user_chat_list_group_name


class ChatListConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=ChatWebSocketCloseCode.UNAUTHORIZED)
            return

        self.group_name = user_chat_list_group_name(self.user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def new_message(self, event):
        await self.send_json(
            {
                "type": ChatWebSocketServerEventType.NEW_MESSAGE,
                "message": event["message"],
            }
        )


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=ChatWebSocketCloseCode.UNAUTHORIZED)
            return

        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.chat_group_name = chat_group_name(self.chat_id)

        is_member = await self._is_user_in_chat(self.user, self.chat_id)
        if not is_member:
            await self.close(code=ChatWebSocketCloseCode.NOT_A_PARTICIPANT)
            return

        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive_json(self, content):
        event_type = content.get("type")

        match event_type:
            case ChatWebSocketClientEventType.TYPING:
                await self.channel_layer.group_send(
                    self.chat_group_name,
                    {
                        "type": ChatWebSocketServerEventType.USER_TYPING,
                        "user": UserWebSocketSerializer(self.user).data,
                    },
                )
            case ChatWebSocketClientEventType.STOP_TYPING:
                await self.channel_layer.group_send(
                    self.chat_group_name,
                    {
                        "type": ChatWebSocketServerEventType.USER_STOP_TYPING,
                        "user": UserWebSocketSerializer(self.user).data,
                    },
                )

    @database_sync_to_async
    def _is_user_in_chat(self, user, chat_id):
        return ChatService.is_user_in_chat(user, chat_id)

    async def new_message(self, event):
        await self.send_json(
            {
                "type": ChatWebSocketServerEventType.NEW_MESSAGE,
                "message": event["message"],
            }
        )

    async def user_typing(self, event):
        if event["user"]["id"] != self.user.id:
            await self.send_json(
                {
                    "type": ChatWebSocketClientEventType.TYPING,
                    "user": event["user"],
                }
            )

    async def user_stop_typing(self, event):
        if event["user"]["id"] != self.user.id:
            await self.send_json(
                {
                    "type": ChatWebSocketClientEventType.STOP_TYPING,
                    "user": event["user"],
                }
            )
