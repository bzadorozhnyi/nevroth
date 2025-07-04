import jsonschema

from datetime import timedelta

from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse
from django.utils import timezone

from accounts.tests.factories.user import MemberFactory
from habits.models import HabitProgress
from habits.tests.factories.habit import (
    HabitFactory,
    UserHabitFactory,
    HabitProgressFactory,
)

streak_schema = {
    "type": "object",
    "properties": {
        "current": {"type": "integer", "minimum": 0},
        "max": {"type": "integer", "minimum": 0},
    },
    "required": ["current", "max"],
    "additionalProperties": False,
}


class HabitProgressStreaksTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.habit = HabitFactory()

        # simulate that user selected habit
        UserHabitFactory(habit=cls.habit, user=cls.member)

        cls.streaks_url = "habit-progress-streak"

    def test_retrieve_habit_progress_streaks_authentication_required(self):
        """Test that authentication is required to retrieve habit progress streaks."""
        url = reverse(self.streaks_url, kwargs={"habit_id": self.habit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _setup_test_date_range(self, status_progress):
        # clear habits progress
        HabitProgress.objects.all().delete()

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=len(status_progress) - 1)

        for i, status_tag in enumerate(status_progress):
            # simulate: user skip day
            if status_tag == "E":
                continue

            current_date = start_date + timedelta(days=i)

            instance = HabitProgressFactory(
                user=self.member,
                habit=self.habit,
                status=HabitProgress.Status.SUCCESS
                if status_tag == "S"
                else HabitProgress.Status.FAIL,
            )
            HabitProgress.objects.filter(pk=instance.pk).update(date=current_date)

    def test_retrieve_habit_progress_streaks_success(self):
        """Test that habit progress streaks are retrieved."""
        self.client.force_authenticate(user=self.member)

        # S - success, F - fail, E - empty, meaning user skip day
        streaks_test_cases = [
            ([], 0, 0),
            (["F"], 0, 0),
            (["S"], 1, 1),
            (["F", "S"], 1, 1),
            (["S", "F"], 0, 1),
            (["E", "E", "S"], 1, 1),
            (["S", "S", "S", "S", "F", "S", "S"], 2, 4),
            (["S", "F", "F", "S", "F", "S", "S", "S"], 3, 3),
            (["S", "F", "S", "S", "F", "S", "F"], 0, 2),
            (["S", "S", "E", "E", "S"], 1, 2),
            (["S", "E", "F", "F", "S", "S", "E"], 0, 2),
            (["S", "E", "F", "F", "S", "S", "E", "E"], 0, 2),
        ]

        for (
            status_progress,
            expected_current_streak,
            expected_max_streak,
        ) in streaks_test_cases:
            with self.subTest(f"status progress {''.join(status_progress)}"):
                self._setup_test_date_range(status_progress)

                url = reverse(self.streaks_url, kwargs={"habit_id": self.habit.id})
                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)

                # Verify response schema
                self._assert_streak_response_schema(response.data)

                results = response.get("results", response.data)

                self.assertEqual(results["current"], expected_current_streak)
                self.assertEqual(results["max"], expected_max_streak)

    def _assert_streak_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=streak_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
