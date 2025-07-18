from rest_framework.test import APITestCase

from chats.tests.factories.chat import (
    ChatFactory,
    ChatPrivateFactory,
    ChatMemberFactory,
    PrivateChatCreatePayloadFactory,
)
from chats.tests.factories.chat_message import (
    ChatMessageFactory,
    ChatMessageCreatePayloadFactory,
    ChatMessageUpdatePayloadFactory,
)


class TestFactories(APITestCase):
    def test_chat_factories(self):
        ChatFactory()
        ChatPrivateFactory()
        ChatMemberFactory()
        PrivateChatCreatePayloadFactory()

    def test_chat_message_factories(self):
        ChatMessageFactory()
        ChatMessageCreatePayloadFactory()
        ChatMessageUpdatePayloadFactory()
