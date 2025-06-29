from rest_framework.test import APITestCase

from habits.tests.factories.habit import (HabitFactory, HabitCreatePayloadFactory, HabitProgressFactory,
                                          HabitProgressSuccessFactory, HabitProgressFailFactory,
                                          HabitProgressCreatePayloadFactory)


class TestFactories(APITestCase):

    def test_habit_factories(self):
        HabitFactory()
        HabitCreatePayloadFactory()
        HabitProgressFactory()
        HabitProgressSuccessFactory()
        HabitProgressFailFactory()
        HabitProgressCreatePayloadFactory()
