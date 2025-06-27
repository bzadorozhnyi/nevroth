from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from habits.models import Habit
from habits.tests.factories.habit import HabitFactory


class HabitSearchFilterTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.list_url = reverse("habit-list")

        # Remove default habits
        Habit.objects.all().delete()

    def test_list_habits_with_search(self):
        self.client.force_authenticate(user=self.member)

        HabitFactory(name="Bad Habit", description="Evil habit")
        HabitFactory(name="Standard Habit", description="Regular bad habit")
        HabitFactory(name="Different Habit", description="Another habit")

        search_test_cases = [
            ("Bad", 2, ["Bad Habit", "Regular bad habit"]),
            ("Different", 1, ["Another habit"]),
        ]

        for search_term, expected_count, expected_values in search_test_cases:
            with self.subTest(f"searching for '{search_term}'"):
                response = self.client.get(f"{self.list_url}?search={search_term}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.get("results", response.data)
                self.assertEqual(len(results), expected_count)

                if search_term == "Bad":
                    self.assertTrue(any(habit["name"] == expected_values[0] for habit in results))
                    self.assertTrue(any(habit["description"] == expected_values[1] for habit in results))
                elif search_term == "Different":
                    self.assertEqual(results[0]["description"], expected_values[0])

    def test_list_habits_with_filter(self):
        self.client.force_authenticate(user=self.member)

        HabitFactory(name="Apple addiction", description="Addiction to fruit")
        HabitFactory(name="Pear addiction", description="Addicted to specific fruit")
        HabitFactory(name="Specific habit", description="Individual habit")

        filter_test_cases = [
            ("name", "Apple", 1),
            ("name", "addiction", 2),
            ("name", "specific", 1),
        ]

        for param, value, expected_count in filter_test_cases:
            with self.subTest(f"filtering for {param}={value}"):
                response = self.client.get(f"{self.list_url}?{param}={value}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.get("results", response.data)
                self.assertEqual(len(results), expected_count)

                if param == "name" and value == "Apple":
                    self.assertEqual(results[0]["name"], "Apple addiction")
                elif param == "name" and value == "specific":
                    self.assertEqual(results[0]["name"], "Specific habit")
