from rest_framework.test import APITestCase

from habits.tests.factories.habit import (
    HabitFactory,
    HabitCreatePayloadFactory,
    HabitProgressFactory,
    HabitProgressSuccessFactory,
    HabitProgressFailFactory,
    HabitProgressCreatePayloadFactory,
    UserHabitFactory,
)


class TestFactories(APITestCase):
    def test_habit_factories(self):
        HabitFactory()
        HabitCreatePayloadFactory()
        UserHabitFactory()
        HabitProgressFactory()
        HabitProgressSuccessFactory()
        HabitProgressFailFactory()
        HabitProgressCreatePayloadFactory()
