import uuid

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

from django.test.testcases import TransactionTestCase

from rest_framework_simplejwt.tokens import AccessToken

from accounts.tests.factories.user import MemberFactory
from nevroth.asgi import application


class ChatConsumerTests(TransactionTestCase):
    @classmethod
    def setUp(cls):
        cls.application = application

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
