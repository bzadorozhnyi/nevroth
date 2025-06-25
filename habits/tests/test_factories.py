from rest_framework.test import APITestCase

from habits.tests.factories.habit import (HabitFactory, HabitCreatePayloadFactory)


class TestFactories(APITestCase):

    def test_habit_factories(self):
        HabitFactory()
        HabitCreatePayloadFactory()
