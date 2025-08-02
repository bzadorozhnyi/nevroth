import factory
from factory.django import DjangoModelFactory

from accounts.tests.factories.user import BaseUserFactory

from faker import Faker

from notifications.models import NotificationMessage
from notifications.tests.factories.helpers import generate_s3_path

faker = Faker()


class NotificationMessageFactory(DjangoModelFactory):
    class Meta:
        model = NotificationMessage

    sender = factory.SubFactory(BaseUserFactory)
    text = factory.LazyAttribute(lambda o: faker.text())
    image_path = generate_s3_path()
