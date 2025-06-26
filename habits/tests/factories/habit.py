import factory
from factory.django import DjangoModelFactory

from habits.models import Habit
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
