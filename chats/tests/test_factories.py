from rest_framework.test import APITestCase

from chats.tests.factories.chat import (
    ChatFactory,
    ChatPrivateFactory,
    ChatMemberFactory,
    PrivateChatCreatePayloadFactory,
)


class TestFactories(APITestCase):
    def test_chat_factories(self):
        ChatFactory()
        ChatPrivateFactory()
        ChatMemberFactory()
        PrivateChatCreatePayloadFactory()
