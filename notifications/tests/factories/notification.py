import factory
from factory.django import DjangoModelFactory

from accounts.tests.factories.user import BaseUserFactory

from faker import Faker

from habits.tests.factories.habit import HabitFactory
from notifications.models import Notification
from notifications.tests.factories.message import MessageFactory

faker = Faker()


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    recipient = factory.SubFactory(BaseUserFactory)
    message = factory.SubFactory(MessageFactory)


class NotificationCreateForUserPayloadFactory(factory.Factory):
    class Meta:
        model = dict

    recipient = factory.SubFactory(BaseUserFactory)
    text = factory.LazyAttribute(lambda o: faker.text())


class NotificationCreateByHabitsPayloadFactory(factory.Factory):
    class Meta:
        model = dict

    text = factory.LazyAttribute(lambda o: faker.text())

    @factory.lazy_attribute
    def habits_ids(self):
        habit_count = getattr(self, "habits_count", 0)
        return [habit.id for habit in HabitFactory.create_batch(habit_count)]
