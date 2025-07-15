import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from habits.tests.factories.habit import UserHabitFactory, HabitFactory

user_search_result_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "full_name": {"type": "string"},
        "relation_status": {
            "type": "string",
            "enum": ["not_friends", "pending_incoming", "pending_outgoing", "friends"],
        },
    },
    "required": ["id", "full_name", "relation_status"],
    "additionalProperties": False,
}

user_search_result_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"]},
        "previous": {"type": ["string", "null"]},
        "results": {
            "type": "array",
            "items": user_search_result_schema,
        },
    },
    "required": ["count", "next", "previous", "results"],
    "additionalProperties": False,
}


class UsersSearchTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = MemberFactory()
        cls.url = reverse("users")

    def test_user_search_authentication_required(self):
        """Test that authentication is required to search users"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_users_by_name_and_filter_by_habits(self):
        """Test user search by full_name and filter by shared habits."""
        self.client.force_authenticate(user=self.user)

        habit1 = HabitFactory()
        habit2 = HabitFactory()

        user1 = MemberFactory(full_name="Alice Johnson")
        user2 = MemberFactory(full_name="Bob Jackson")
        user3 = MemberFactory(full_name="Charlie")

        UserHabitFactory(user=user1, habit=habit1)

        UserHabitFactory(user=user2, habit=habit2)

        UserHabitFactory(user=user3, habit=habit1)
        UserHabitFactory(user=user3, habit=habit2)

        test_cases = [
            {
                "description": "search by full_name",
                "params": {"query": "alice"},
                "expected_names": ["Alice Johnson"],
            },
            {
                "description": "filter by single habit",
                "params": {"habits": str(habit2.id)},
                "expected_names": ["Bob Jackson", "Charlie"],
            },
            {
                "description": "filter by multiple habits",
                "params": {"habits": f"{habit1.id},{habit2.id}"},
                "expected_names": ["Alice Johnson", "Bob Jackson", "Charlie"],
            },
            {
                "description": "combined search and filter",
                "params": {"query": "charlie", "habits": f"{habit2.id}"},
                "expected_names": ["Charlie"],
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                response = self.client.get(self.url, case["params"])
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                result_names = [user["full_name"] for user in response.data["results"]]
                self.assertCountEqual(result_names, case["expected_names"])

                for expected_name in case["expected_names"]:
                    self.assertIn(expected_name, result_names)

                self._assert_list_response_schema(response.data)

    def test_paginated_users_multiple_pages(self):
        """Test that users are listed with correct pagination over multiple pages."""
        self.client.force_authenticate(self.user)

        MemberFactory.create_batch(15)

        # check first page
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["count"], 15)
        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

        # check second page
        next_url = data["next"]
        response2 = self.client.get(next_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data2 = response2.data
        self.assertEqual(len(data2["results"]), 5)
        self.assertIsNone(data2["next"])
        self.assertIsNotNone(data2["previous"])

        # Verify response schemas
        self._assert_list_response_schema(data)
        self._assert_list_response_schema(data2)

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(
                instance=data, schema=user_search_result_list_response_schema
            )
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
