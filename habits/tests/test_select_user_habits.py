from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory, AdminFactory
from habits.models import Habit, UserHabit
from habits.tests.factories.habit import HabitFactory


class SelectUserHabitsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.admin = AdminFactory()

        # Remove default habits
        Habit.objects.all().delete()
        cls.habits = HabitFactory.create_batch(5)

        cls.url = reverse("habit-select-habits")

    def test_authentication_required(self):
        """Test that authentication is required."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_selecting_habits_success(self, habits_ids):
        payload = {
            "habits_ids": habits_ids,
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual_habits_ids = list(
            UserHabit.objects.filter(user=self.member).values_list(
                "habit_id", flat=True
            )
        )
        self.assertCountEqual(actual_habits_ids, habits_ids)

    def test_select_user_habits_as_member(self):
        """Test that member can select habits."""
        self.client.force_authenticate(self.member)
        habits_ids = [habit.id for habit in self.habits[:3]]
        self._test_selecting_habits_success(habits_ids)

    def test_cannot_select_user_habits_as_admin(self):
        """Test that admin cannot select habits."""
        self.client.force_authenticate(self.admin)
        habits_ids = [habit.id for habit in self.habits[:3]]
        payload = {
            "habits_ids": habits_ids,
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_select_less_than_three_habits(self):
        """Test that cannot select less than three habits."""
        self.client.force_authenticate(self.member)

        # 1 habit selected
        habits_ids = [self.habits[0].id]
        payload = {
            "habits_ids": habits_ids,
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_select_more_than_three_habits(self):
        """Test that cannot select more than three habits."""
        self.client.force_authenticate(self.member)

        # 5 habits selected
        habits_ids = [habit.id for habit in self.habits[:5]]
        payload = {
            "habits_ids": habits_ids,
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_select_non_unique_habits(self):
        """Test that cannot select non-unique habits."""
        self.client.force_authenticate(self.member)

        # First and last are the same
        habits_ids = [self.habits[i].id for i in [0, 1, 0]]
        payload = {
            "habits_ids": habits_ids,
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_select_non_existing_habits(self):
        """Test that cannot select non-existing habits."""
        self.client.force_authenticate(self.member)

        # Last id does not exist
        habits_ids = [habit.id for habit in self.habits[:2]] + [123456789]
        payload = {
            "habits_ids": habits_ids,
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_selected_habits(self):
        """Test that habits can be updated."""
        self.client.force_authenticate(self.member)
        # Create habits
        habits_ids = [habit.id for habit in self.habits[:3]]
        self._test_selecting_habits_success(habits_ids)

        # Update habits
        new_habits_ids = [habit.id for habit in self.habits[2:5]]
        self._test_selecting_habits_success(new_habits_ids)
