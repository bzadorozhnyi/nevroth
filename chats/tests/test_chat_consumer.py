import jsonschema
import uuid

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

from django.test.testcases import TransactionTestCase
from django.urls import reverse

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import status
from rest_framework.test import APIClient

from accounts.tests.factories.user import MemberFactory
from chats.tests.factories.chat import ChatPrivateFactory, ChatMemberFactory
from chats.tests.factories.chat_message import ChatMessageCreatePayloadFactory
from nevroth.asgi import application

from asgiref.sync import sync_to_async

chat_message_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "content": {"type": "string", "minLength": 1, "maxLength": 256},
        "sender": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "minimum": 1},
                "full_name": {"type": "string", "minLength": 1, "maxLength": 256},
            },
            "required": ["id", "full_name"],
            "additionalProperties": False,
        },
    },
    "required": ["id", "content", "sender"],
    "additionalProperties": False,
}

chat_new_message_event_schema = {
    "type": "object",
    "properties": {
        "type": {"const": "new_message"},
        "message": chat_message_schema,
    },
    "required": ["type", "message"],
    "additionalProperties": False,
}

chat_list_message_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "chat": {"type": "integer", "minimum": 1},
        "content": {"type": "string", "minLength": 1, "maxLength": 256},
        "sender": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "minimum": 1},
                "full_name": {"type": "string", "minLength": 1, "maxLength": 256},
            },
            "required": ["id", "full_name"],
            "additionalProperties": False,
        },
    },
    "required": ["id", "chat", "content", "sender"],
    "additionalProperties": False,
}

chat_list_new_message_event_schema = {
    "type": "object",
    "properties": {
        "type": {"const": "new_message"},
        "message": chat_list_message_schema,
    },
    "required": ["type", "message"],
    "additionalProperties": False,
}


class ChatConsumerTests(TransactionTestCase):
    @classmethod
    def setUp(cls):
        cls.application = application
        cls.list_url = reverse("chat-message-list")

    async def test_websocket_connect_authentication_required(self):
        """Test that authentication is required for websocket connect."""

        communicator = WebsocketCommunicator(
            self.application,
            "ws/chats/123/",
        )

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_query_param_auth_websocket_connect_and_disconnect(self):
        """Test that authentication through query params works as expected."""
        user = await database_sync_to_async(MemberFactory)()
        token = AccessToken.for_user(user)

        chat = await database_sync_to_async(ChatPrivateFactory)()
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=user)

        communicator = WebsocketCommunicator(
            self.application,
            f"ws/chats/{chat.id}/?token={token}",
        )

        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_headers_auth_websocket_connect_and_disconnect(self):
        """Test that authentication through headers works as expected."""
        user = await database_sync_to_async(MemberFactory)()
        token = AccessToken.for_user(user)

        chat = await database_sync_to_async(ChatPrivateFactory)()
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=user)

        communicator = WebsocketCommunicator(
            application,
            f"ws/chats/{chat.id}/",
            headers=[
                (b"authorization", f"Bearer {token}".encode("utf-8")),
            ],
        )

        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_cannot_connect_with_invalid_token(self):
        """Test that cannot connect with invalid token."""
        user = await database_sync_to_async(MemberFactory)()
        fake_token = str(uuid.uuid4())

        chat = await database_sync_to_async(ChatPrivateFactory)()
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=user)

        communicator = WebsocketCommunicator(
            application,
            f"ws/chats/{chat.id}/",
            headers=[
                (b"authorization", f"Bearer {fake_token}".encode("utf-8")),
            ],
        )

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_cannot_connect_if_user_is_not_chat_member(self):
        """Test that cannot connect with if user is not chat member."""
        user = await database_sync_to_async(MemberFactory)()
        token = AccessToken.for_user(user)

        chat = await database_sync_to_async(ChatPrivateFactory)()
        communicator = WebsocketCommunicator(
            application,
            f"ws/chats/{chat.id}/",
            headers=[
                (b"authorization", f"Bearer {token}".encode("utf-8")),
            ],
        )

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_new_message_broadcast(self):
        """Test that new messages are broadcast to all connected users."""

        sender = await database_sync_to_async(MemberFactory)()
        receiver = await database_sync_to_async(MemberFactory)()

        sender_token = AccessToken.for_user(sender)
        receiver_token = AccessToken.for_user(receiver)

        # add sender and receiver to chat
        chat = await database_sync_to_async(ChatPrivateFactory)()
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=sender)
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=receiver)

        # connect receiver to websocket
        communicator = WebsocketCommunicator(
            application,
            f"ws/chats/{chat.id}/",
            headers=[
                (b"authorization", f"Bearer {receiver_token}".encode("utf-8")),
            ],
        )

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # sender send message
        client = APIClient()
        client.force_authenticate(user=sender, token=sender_token)

        payload = await database_sync_to_async(ChatMessageCreatePayloadFactory)(
            chat=chat.id
        )
        response = await sync_to_async(client.post)(self.list_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = await communicator.receive_json_from()
        message = response["message"]

        self.assertEqual(message["sender"]["id"], sender.id)
        self.assertEqual(message["sender"]["full_name"], sender.full_name)
        self.assertEqual(message["content"], payload["content"])

        self._assert_new_message_event_schema(response)

        await communicator.disconnect()

    async def test_typing_and_stop_typing(self):
        """Test that typing and stopping typing works as expected."""
        user1 = await database_sync_to_async(MemberFactory)()
        user2 = await database_sync_to_async(MemberFactory)()

        chat = await database_sync_to_async(ChatPrivateFactory)()
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=user1)
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=user2)

        user1_token = AccessToken.for_user(user1)
        user1_communicator = WebsocketCommunicator(
            application,
            f"ws/chats/{chat.id}/",
            headers=[
                (b"authorization", f"Bearer {user1_token}".encode("utf-8")),
            ],
        )
        connected, _ = await user1_communicator.connect()
        self.assertTrue(connected)

        user2_token = AccessToken.for_user(user2)
        user2_communicator = WebsocketCommunicator(
            application,
            f"ws/chats/{chat.id}/",
            headers=[
                (b"authorization", f"Bearer {user2_token}".encode("utf-8")),
            ],
        )
        connected, _ = await user2_communicator.connect()
        self.assertTrue(connected)

        # user1 sends "typing"
        await user1_communicator.send_json_to({"type": "typing"})
        response = await user2_communicator.receive_json_from()
        self.assertEqual(response["type"], "typing")
        self.assertEqual(response["user"]["id"], user1.id)

        # user1 sends "stop_typing"
        await user1_communicator.send_json_to({"type": "stop_typing"})
        response = await user2_communicator.receive_json_from()
        self.assertEqual(response["type"], "stop_typing")
        self.assertEqual(response["user"]["id"], user1.id)

        await user1_communicator.disconnect()
        await user2_communicator.disconnect()

    async def test_chat_list_consumer_receives_new_message(self):
        """Test that ChatListConsumer receives new message event when a message is sent."""
        sender = await database_sync_to_async(MemberFactory)()
        receiver = await database_sync_to_async(MemberFactory)()

        chat = await database_sync_to_async(ChatPrivateFactory)()
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=sender)
        await database_sync_to_async(ChatMemberFactory)(chat=chat, user=receiver)

        sender_token = AccessToken.for_user(sender)
        receiver_token = AccessToken.for_user(receiver)

        # connect receiver to ChatListConsumer
        chat_list_communicator = WebsocketCommunicator(
            application,
            "ws/chat-list/",
            headers=[(b"authorization", f"Bearer {receiver_token}".encode("utf-8"))],
        )
        connected, _ = await chat_list_communicator.connect()
        self.assertTrue(connected)

        # sender sends message
        client = APIClient()
        client.force_authenticate(user=sender, token=sender_token)

        payload = await database_sync_to_async(ChatMessageCreatePayloadFactory)(
            chat=chat.id
        )
        response = await sync_to_async(client.post)(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # receiver gets update via chat list socket
        response = await chat_list_communicator.receive_json_from()

        self.assertEqual(response["type"], "new_message")
        message = response["message"]

        self.assertEqual(message["chat"], chat.id)
        self.assertEqual(message["sender"]["id"], sender.id)
        self.assertEqual(message["content"], payload["content"])

        self._assert_chat_list_new_message_event_schema(response)

        await chat_list_communicator.disconnect()

    def _assert_new_message_event_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=chat_new_message_event_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")

    def _assert_chat_list_new_message_event_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(
                instance=data, schema=chat_list_new_message_event_schema
            )
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
