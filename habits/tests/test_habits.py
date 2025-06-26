import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import (MemberFactory, AdminFactory)
from habits.models import Habit
from habits.tests.factories.habit import HabitFactory, HabitCreatePayloadFactory

habit_detail_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "description": {"type": "string"},
    },
    "required": ["id", "name", "description"],
    "additionalProperties": False,
}

habit_list_schema = {
    "type": "array",
    "items": habit_detail_schema,
}


class HabitTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.admin = AdminFactory()

        # Remove default habits
        Habit.objects.all().delete()
        cls.habits = HabitFactory.create_batch(5)

        cls.list_url = reverse("habit-list")
        cls.detail_url = "habit-detail"

    def test_list_habits_authentication_required(self):
        """Test that authentication is required to list habits."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_list_habits_as_authenticated_user(self):
        """Test that authenticated user can list all habits."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data

        # Should see all habits
        expected_count = len(self.habits)
        self.assertEqual(len(result), expected_count)

        # Verify response schema
        self._assert_list_response_schema(response.data)

    def test_list_habits_as_member(self):
        """Test that member can list all habits."""
        self.client.force_authenticate(self.member)
        self._test_list_habits_as_authenticated_user()

    def test_list_habits_as_admin(self):
        """Test that admin can list all habits."""
        self.client.force_authenticate(self.admin)
        self._test_list_habits_as_authenticated_user()

    def test_retrieve_habit_authentication_required(self):
        """Test that authentication is required to retrieve a habit."""
        url = reverse("habit-detail", kwargs={"pk": self.habits[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_retrieve_habit_as_authenticated_user(self):
        """Test that authenticated user can retrieve a habit."""
        url = reverse("habit-detail", kwargs={"pk": self.habits[0].pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data
        self.assertEqual(result["id"], self.habits[0].pk)
        self.assertEqual(result["name"], self.habits[0].name)
        self.assertEqual(result["description"], self.habits[0].description)

        self._assert_detail_response_schema(response.data)

    def test_retrieve_habit_as_member(self):
        """Test that member can retrieve a habit."""
        self.client.force_authenticate(self.member)
        self._test_retrieve_habit_as_authenticated_user()

    def test_retrieve_habit_as_admin(self):
        """Test that admin can retrieve a habit."""
        self.client.force_authenticate(self.admin)
        self._test_retrieve_habit_as_authenticated_user()

    def test_create_habit_authentication_required(self):
        """Test that authentication is required to create a new habit."""
        payload = HabitCreatePayloadFactory()
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_create_habit_as_member(self):
        """Test that member cannot create a new habit."""
        self.client.force_authenticate(self.member)

        payload = HabitCreatePayloadFactory()
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_habit_as_admin(self):
        """Test that admin can create a new habit."""
        self.client.force_authenticate(self.admin)

        payload = HabitCreatePayloadFactory()
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(Habit.objects.filter(id=response.data["id"]).exists())

        habit = Habit.objects.get(id=response.data["id"])
        self.assertEqual(habit.name, payload["name"])
        self.assertEqual(habit.description, payload["description"])

        self._assert_detail_response_schema(response.data)

    def test_cannot_create_habit_without_required_fields(self):
        """Test that habit cannot be created without required fields."""
        self.client.force_authenticate(self.admin)

        payload = {
            "name": "just_name"
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_habit_with_empty_name(self):
        """Test that habit cannot be created with empty name."""
        self.client.force_authenticate(self.admin)

        payload = HabitCreatePayloadFactory()
        payload["name"] = ""

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_habit_with_empty_description(self):
        """Test that habit cannot be created with empty description."""
        self.client.force_authenticate(self.admin)

        payload = HabitCreatePayloadFactory()
        payload["description"] = ""

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_habit_authentication_required(self):
        """Test that authentication is required to update a new habit."""
        update_payload = {
            "name": "new_name",
            "description": "new_description",
        }

        response = self.client.put(self.list_url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_update_habit_as_member(self):
        """Test that member cannot update habit."""
        self.client.force_authenticate(self.member)

        url = reverse(self.detail_url, kwargs={"pk": self.habits[0].pk})
        update_payload = {
            "name": "new_name",
            "description": "new_description",
        }

        response = self.client.put(url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_habit_as_admin(self):
        """Test that admin can update habit."""
        self.client.force_authenticate(self.admin)

        url = reverse(self.detail_url, kwargs={"pk": self.habits[0].pk})
        update_payload = {
            "name": "new_name",
            "description": "new_description",
        }

        response = self.client.put(url, update_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_detail_response_schema(response.data)

        # Verify habit was updated
        self.habits[0].refresh_from_db()
        self.assertEqual(self.habits[0].name, update_payload["name"])
        self.assertEqual(self.habits[0].description, update_payload["description"])

    def test_cannot_update_habit_with_empty_name(self):
        """Test that habit cannot be updated with empty name."""
        self.client.force_authenticate(self.admin)

        url = reverse(self.detail_url, kwargs={"pk": self.habits[0].pk})
        update_payload = {
            "name": "",
            "description": "new_description",
        }

        response = self.client.put(url, update_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_update_habit_with_empty_description(self):
        """Test that habit cannot be updated with empty description."""
        self.client.force_authenticate(self.admin)

        url = reverse(self.detail_url, kwargs={"pk": self.habits[0].pk})
        update_payload = {
            "name": "new_name",
            "description": "",
        }

        response = self.client.put(url, update_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_habit_authentication_required(self):
        """Test that authentication is required to delete a habit."""
        url = reverse(self.detail_url, kwargs={"pk": self.habits[0].pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_delete_habit_as_member(self):
        """Test that member cannot delete habit."""
        self.client.force_authenticate(self.member)
        url = reverse(self.detail_url, kwargs={"pk": self.habits[0].pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_habit_as_admin(self):
        """Test that admin can delete habit."""
        self.client.force_authenticate(self.admin)

        habit_to_delete = self.habits[0]

        url = reverse(self.detail_url, kwargs={"pk": habit_to_delete.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=habit_to_delete.pk).exists())

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=habit_list_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")

    def _assert_detail_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=habit_detail_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
