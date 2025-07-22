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

message_schema = {
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

new_message_event_schema = {
    "type": "object",
    "properties": {
        "type": {"const": "new_message"},
        "message": message_schema,
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

        communicator = WebsocketCommunicator(
            self.application,
            f"ws/chats/123/?token={token}",
        )

        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_headers_auth_websocket_connect_and_disconnect(self):
        """Test that authentication through headers works as expected."""
        user = await database_sync_to_async(MemberFactory)()
        token = AccessToken.for_user(user)

        communicator = WebsocketCommunicator(
            application,
            "ws/chats/123/",
            headers=[
                (b"authorization", f"Bearer {token}".encode("utf-8")),
            ],
        )

        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_cannot_connect_with_invalid_token(self):
        """Test that cannot connect with invalid token."""
        fake_token = str(uuid.uuid4())

        communicator = WebsocketCommunicator(
            application,
            "ws/chats/123/",
            headers=[
                (b"authorization", f"Bearer {fake_token}".encode("utf-8")),
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

    def _assert_new_message_event_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=new_message_event_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
