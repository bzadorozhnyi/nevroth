from channels.testing import WebsocketCommunicator

from django.test.testcases import TestCase

from nevroth.asgi import application


class ChatConsumerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.application = application

    async def test_websocket_connect_and_disconnect(self):
        communicator = WebsocketCommunicator(
            self.application,
            "ws/chats/123/",
        )

        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()
