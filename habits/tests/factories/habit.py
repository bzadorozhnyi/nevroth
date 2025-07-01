import factory
from factory.django import DjangoModelFactory

from accounts.tests.factories.user import BaseUserFactory
from habits.models import Habit, HabitProgress, UserHabit
from faker import Faker

faker = Faker()


class HabitFactory(DjangoModelFactory):
    class Meta:
        model = Habit

    name = factory.Sequence(lambda n: f"Habit {n}")
    description = factory.LazyFunction(lambda: faker.sentence(nb_words=10))


class HabitCreatePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    name = factory.Sequence(lambda n: f"Habit {n}")
    description = factory.LazyFunction(lambda: faker.sentence(nb_words=10))


class UserHabitFactory(DjangoModelFactory):
    class Meta:
        model = UserHabit

    user = factory.SubFactory(BaseUserFactory)
    habit = factory.SubFactory(HabitFactory)


class HabitProgressFactory(DjangoModelFactory):
    class Meta:
        model = HabitProgress

    user = factory.SubFactory(BaseUserFactory)
    habit = factory.SubFactory(HabitFactory)


class HabitProgressSuccessFactory(HabitProgressFactory):
    status = HabitProgress.Status.SUCCESS


class HabitProgressFailFactory(HabitProgressFactory):
    status = HabitProgress.Status.FAIL


class HabitProgressCreatePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    habit = factory.LazyAttribute(lambda o: HabitFactory().id)
    status = factory.Iterator([HabitProgress.Status.FAIL, HabitProgress.Status.SUCCESS])
