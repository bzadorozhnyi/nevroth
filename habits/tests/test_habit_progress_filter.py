from collections import Counter
from datetime import date, timedelta

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory, AdminFactory
from habits.models import Habit, HabitProgress
from habits.tests.factories.habit import HabitFactory, HabitProgressFactory


class HabitProgressFilterTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()

        # Remove default habits
        Habit.objects.all().delete()
        cls.habits = HabitFactory.create_batch(3)

        cls.url = reverse("habit-progress")

    def _setup_test_date_range(self, user):
        # 25 26 27 28 29 (day)
        #  S  F  S  F  S (S - success, F - fail)

        start_date = date(2025, 6, 25)
        end_date = date(2025, 6, 29)

        for i in range((end_date - start_date).days + 1):
            current_date = start_date + timedelta(days=i)

            instance = HabitProgressFactory(
                user=user,
                habit=self.habits[0],
                status=HabitProgress.Status.SUCCESS if i % 2 == 0 else HabitProgress.Status.FAIL,
            )
            HabitProgress.objects.filter(pk=instance.pk).update(date=current_date)

    def test_list_habits_progress_with_filter(self):
        self.client.force_authenticate(self.member)
        self._setup_test_date_range(self.member)

        filter_test_cases = [
            ({"date": "2025-06-25"}, 1, (1, 0)),
            ({"from_date": "2025-06-26"}, 4, (2, 2)),
            ({"to_date": "2025-06-29"}, 5, (3, 2)),
            ({"from_date": "2025-06-26", "to_date": "2025-06-28"}, 3, (1, 2)),
            ({"from_date": "2025-06-28", "to_date": "2025-06-25"}, 0, (0, 0)),  # invalid range
        ]

        for param_value, expected_count, (expected_success_count, expected_fail_count) in filter_test_cases:
            filter_param = "&".join(f"{k}={v}" for k, v in param_value.items())
            with self.subTest(f"filter by {filter_param}"):
                response = self.client.get(f"{self.url}?{filter_param}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.get("results", response.data)
                self.assertEqual(len(results), expected_count)

                counts = Counter(item["status"] for item in results)

                self.assertEqual(expected_success_count, counts["success"])
                self.assertEqual(expected_fail_count, counts["fail"])
