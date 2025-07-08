import factory
from factory.django import DjangoModelFactory

from accounts.tests.factories.user import BaseUserFactory

from faker import Faker

from notifications.models import Message

faker = Faker()


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    sender = factory.SubFactory(BaseUserFactory)
    text = factory.LazyAttribute(lambda o: faker.text())
