from channels.routing import URLRouter
from chats.consumers import ChatConsumer
from channels.testing import WebsocketCommunicator

from django.test.testcases import TestCase
from django.urls import re_path


class ChatConsumerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.application = URLRouter(
            [
                re_path(r"ws/chats/(?P<chat_id>\d+)/$", ChatConsumer.as_asgi()),
            ]
        )

    async def test_websocket_connect_and_disconnect(self):
        communicator = WebsocketCommunicator(
            self.application,
            "ws/chats/123/",
        )

        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()
