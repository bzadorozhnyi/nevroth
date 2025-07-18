import factory
from factory.django import DjangoModelFactory

from accounts.tests.factories.user import BaseUserFactory
from chats.models import ChatMessage
from chats.tests.factories.chat import ChatFactory

from faker import Faker

faker = Faker()


class ChatMessageFactory(DjangoModelFactory):
    class Meta:
        model = ChatMessage

    chat = factory.SubFactory(ChatFactory)
    content = factory.LazyFunction(lambda: faker.sentence(nb_words=10))
    sender = factory.SubFactory(BaseUserFactory)


class ChatMessageCreatePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    chat = factory.LazyAttribute(lambda o: ChatFactory().id)
    content = factory.LazyFunction(lambda: faker.sentence(nb_words=10))


class ChatMessageUpdatePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    content = factory.LazyFunction(lambda: faker.sentence(nb_words=10))
