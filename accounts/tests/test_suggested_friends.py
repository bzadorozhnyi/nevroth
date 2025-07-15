import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from friends.tests.factories.friends_relation import (
    FriendsRelationAcceptedFactory,
    FriendsRelationPendingFactory,
)
from habits.models import Habit
from habits.tests.factories.habit import HabitFactory, UserHabitFactory

user_suggestion_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "full_name": {"type": "string"},
    },
    "required": ["id", "full_name"],
    "additionalProperties": False,
}

suggested_friends_list_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"]},
        "previous": {"type": ["string", "null"]},
        "results": {
            "type": "array",
            "items": user_suggestion_schema,
        },
    },
    "required": ["count", "next", "previous", "results"],
    "additionalProperties": False,
}


class SuggestedFriendsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = MemberFactory()
        cls.url = reverse("suggested-friends-list")

        # remove default habits
        Habit.objects.all().delete()

    def test_suggested_friends_list_authentication_required(self):
        """Test that authentication is required to list suggested friends."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_suggested_friends_list_success(self):
        self.client.force_authenticate(self.user)

        # create 2 habits for self.user
        habit1, habit2 = HabitFactory(), HabitFactory()
        UserHabitFactory(user=self.user, habit=habit1)
        UserHabitFactory(user=self.user, habit=habit2)

        # user1 has both habits — we expect the result
        user1 = MemberFactory()
        UserHabitFactory(user=user1, habit=habit1)
        UserHabitFactory(user=user1, habit=habit2)

        # user2 has only one — we expect as a result
        user2 = MemberFactory()
        UserHabitFactory(user=user2, habit=habit1)

        # user3 has no common habits — we DO NOT expect
        user3 = MemberFactory()
        UserHabitFactory(user=user3, habit=HabitFactory())

        # user4 has one habit in common,
        # but is already friends with self.user - we don't expect it as a result
        user4 = MemberFactory()
        UserHabitFactory(user=user4, habit=habit1)
        FriendsRelationAcceptedFactory(from_user=self.user, to_user=user4)

        # user5 has one habit in common,
        # but has sent friendship request to self.user - we don't expect it as a result
        user5 = MemberFactory()
        UserHabitFactory(user=user5, habit=habit1)
        FriendsRelationPendingFactory(from_user=user5, to_user=self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        returned_ids = {user["id"] for user in results}

        expected_ids = {user1.id, user2.id}

        self.assertSetEqual(expected_ids, returned_ids)
        self._assert_list_response_schema(response.data)

    def test_paginated_suggested_friends_multiple_pages(self):
        self.client.force_authenticate(self.user)

        shared_habit = HabitFactory()
        UserHabitFactory(user=self.user, habit=shared_habit)

        for _ in range(15):
            other_user = MemberFactory()
            UserHabitFactory(user=other_user, habit=shared_habit)

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
            jsonschema.validate(instance=data, schema=suggested_friends_list_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
