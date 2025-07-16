import factory
from factory.django import DjangoModelFactory

from accounts.tests.factories.user import BaseUserFactory
from chats.models import Chat, ChatMember


class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat


class ChatPrivateFactory(ChatFactory):
    chat_type = Chat.ChatType.PRIVATE


class ChatMemberFactory(DjangoModelFactory):
    class Meta:
        model = ChatMember

    chat = factory.SubFactory(ChatFactory)
    user = factory.SubFactory(BaseUserFactory)
