from datetime import datetime, timedelta

import jsonschema

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory, AdminFactory
from habits.models import Habit, HabitProgress
from habits.tests.factories.habit import (
    HabitFactory,
    HabitProgressSuccessFactory,
    HabitProgressCreatePayloadFactory,
    HabitProgressFailFactory,
)

habit_progress_schema = {
    "type": "object",
    "properties": {
        "habit": {"type": "integer"},
        "date": {"type": "string", "format": "date"},
        "status": {"type": "string", "enum": ["success", "fail"]},
    },
    "required": ["habit", "date", "status"],
    "additionalProperties": False,
}

habit_progress_list_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer", "minimum": 0},
        "next": {"type": ["string", "null"], "format": "uri"},
        "previous": {"type": ["string", "null"], "format": "uri"},
        "results": {
            "type": "array",
            "items": habit_progress_schema,
        },
    },
    "required": ["count", "next", "previous", "results"],
    "additionalProperties": False,
}


class HabitProgressTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.admin = AdminFactory()

        # Remove default habits
        Habit.objects.all().delete()
        cls.habits = HabitFactory.create_batch(5)

        cls.url = reverse("habit-progress")

    def test_list_habits_progress_authentication_required(self):
        """Test that authentication is required to get habits progress list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_list_habits_progress_as_authenticated_user(self, user):
        """Test that authenticated user can get habits progress list."""
        self.client.force_authenticate(user)

        HabitProgressSuccessFactory(user=user, habit=self.habits[0])
        HabitProgressSuccessFactory(user=user, habit=self.habits[1])
        HabitProgressSuccessFactory(user=user, habit=self.habits[2])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data

        self.assertEqual(result["count"], 3)
        self.assertIsNone(result["next"])
        self.assertIsNone(result["previous"])
        self.assertEqual(len(result["results"]), 3)

        # Verify response schema
        self._assert_list_response_schema(response.data)

    def test_paginated_list_habits_progress_multiple_pages(self):
        """Test that habits progress are listed with correct pagination over multiple pages."""
        self.client.force_authenticate(self.member)

        # clean up habit progress
        HabitProgress.objects.all().delete()

        HabitProgressSuccessFactory.create_batch(15, user=self.member)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["count"], 15)
        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

        next_url = data["next"]
        response2 = self.client.get(next_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data2 = response2.data
        self.assertEqual(len(data2["results"]), 5)
        self.assertIsNone(data2["next"])
        self.assertIsNotNone(data2["previous"])

        # Verify response schema
        self._assert_list_response_schema(data)
        self._assert_list_response_schema(data2)

    def test_list_habits_progress_as_member(self):
        """Test that member can get habits progress list."""
        self._test_list_habits_progress_as_authenticated_user(self.member)

    def test_list_habits_progress_as_admin(self):
        """Test that admin can get habits progress list."""
        self._test_list_habits_progress_as_authenticated_user(self.admin)

    def test_create_habit_progress_authentication_required(self):
        """Test that authentication is required to create habit progress."""
        payload = HabitProgressCreatePayloadFactory()
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_create_habit_progress_as_authenticated_user(self, user):
        """Test that authenticated user can create habit progress."""
        self.client.force_authenticate(user)

        payload = HabitProgressCreatePayloadFactory()

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            HabitProgress.objects.filter(
                user=user,
                habit=payload["habit"],
            ).exists()
        )

        habit_progress = HabitProgress.objects.filter(
            user=user,
            habit=payload["habit"],
        ).first()

        self.assertEqual(habit_progress.habit.id, payload["habit"])
        self.assertEqual(habit_progress.status, payload["status"])
        self.assertEqual(habit_progress.date, datetime.today().date())

        # Verify response schema
        self._assert_detail_response_schema(response.data)

    def test_create_habit_progress_as_member(self):
        """Test that member can create a new habit progress."""
        self._test_create_habit_progress_as_authenticated_user(self.member)

    def test_create_habit_progress_as_admin(self):
        """Test that admin can create a new habit progress."""
        self._test_create_habit_progress_as_authenticated_user(self.admin)

    def test_cannot_create_habit_progress_without_habit(self):
        """Test that habit progress cannot be created without habit."""
        self.client.force_authenticate(self.member)

        payload = HabitProgressCreatePayloadFactory()
        payload.pop("habit")

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_habit_progress_without_status(self):
        """Test that habit progress cannot be created without status."""
        self.client.force_authenticate(self.member)

        payload = HabitProgressCreatePayloadFactory()
        payload.pop("status")

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_habit_progress_with_nonexisting_status_choice(self):
        """Test that habit progress cannot be created with non-existing status choice."""
        self.client.force_authenticate(self.member)

        payload = HabitProgressCreatePayloadFactory()
        payload["status"] = "nonexistent-status"

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_habit_progress_authentication_required(self):
        """Test that authentication is required to update habit progress."""
        HabitProgressSuccessFactory(user=self.member, habit=self.habits[0])

        update_payload = {
            "status": "fail",
        }
        response = self.client.post(self.url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_update_habit_progress_as_authenticated_user(self, user):
        self.client.force_authenticate(user)

        HabitProgressSuccessFactory(user=self.member, habit=self.habits[0])

        update_payload = {
            "habit": self.habits[0].id,
            "status": "fail",
        }
        response = self.client.post(self.url, update_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            HabitProgress.objects.filter(
                user=user,
                habit=update_payload["habit"],
            ).exists()
        )

        habit_progress = HabitProgress.objects.filter(
            user=user,
            habit=update_payload["habit"],
        ).first()

        self.assertEqual(habit_progress.habit.id, update_payload["habit"])
        self.assertEqual(habit_progress.status, update_payload["status"])
        self.assertEqual(habit_progress.date, datetime.today().date())

        # Verify response schema
        self._assert_detail_response_schema(response.data)

    def test_update_habit_progress_as_member(self):
        """Test that member can update habit progress."""
        self._test_update_habit_progress_as_authenticated_user(self.member)

    def test_update_habit_progress_as_admin(self):
        """Test that admin can update habit progress."""
        self._test_update_habit_progress_as_authenticated_user(self.admin)

    def test_cannot_update_habit_progress_without_status(self):
        """Test that habit progress cannot be updated without status."""
        self.client.force_authenticate(self.member)

        HabitProgressSuccessFactory(user=self.member, habit=self.habits[0])

        update_payload = {
            "habit": self.habits[0].id,
        }

        response = self.client.post(self.url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_update_habit_progress_with_nonexisting_status_choice(self):
        """Test that habit progress cannot be updated with non-existing status choice."""
        self.client.force_authenticate(self.member)

        HabitProgressSuccessFactory(user=self.member, habit=self.habits[0])

        update_payload = {
            "habit": self.habits[0].id,
            "status": "nonexistent-status",
        }

        response = self.client.post(self.url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_update_habit_progress_success(self, update_payload):
        """Test that habit progress update was successful."""
        response = self.client.post(self.url, update_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            HabitProgress.objects.filter(
                user=self.member,
                habit=update_payload["habit"],
            ).exists()
        )

        habit_progress = HabitProgress.objects.filter(
            user=self.member,
            habit=update_payload["habit"],
        ).first()

        self.assertEqual(habit_progress.habit.id, update_payload["habit"])
        self.assertEqual(habit_progress.status, update_payload["status"])
        self.assertEqual(habit_progress.date, datetime.today().date())

        # Verify response schema
        self._assert_detail_response_schema(response.data)

    def test_update_habit_progress_success_to_fail_status_after_5_minutes(self):
        """Test that habit progress can be updated from success to fail status after 5 minutes."""
        self.client.force_authenticate(self.member)

        # last updated - 10 minutes ago
        updated_at = timezone.now() - timedelta(minutes=10)
        instance = HabitProgressSuccessFactory(user=self.member, habit=self.habits[0])
        HabitProgress.objects.filter(pk=instance.pk).update(updated_at=updated_at)

        update_payload = {
            "habit": self.habits[0].id,
            "status": "fail",
        }

        self._test_update_habit_progress_success(update_payload)

    def test_can_update_habit_progress_fail_to_success_status_in_5_minutes(self):
        """Test that habit progress can be updated from fail to success status in 5 minutes."""
        self.client.force_authenticate(self.member)

        # last updated - 2 minutes ago
        updated_at = timezone.now() - timedelta(minutes=2)
        instance = HabitProgressFailFactory(user=self.member, habit=self.habits[0])
        HabitProgress.objects.filter(pk=instance.pk).update(updated_at=updated_at)

        update_payload = {
            "habit": self.habits[0].id,
            "status": "success",
        }

        self._test_update_habit_progress_success(update_payload)

    def test_update_habit_progress_success_to_fail_status_in_5_minutes(self):
        """Test that habit progress can be updated from success to fail status in 5 minutes."""
        self.client.force_authenticate(self.member)

        # last updated - 2 minutes ago
        updated_at = timezone.now() - timedelta(minutes=2)
        instance = HabitProgressSuccessFactory(user=self.member, habit=self.habits[0])
        HabitProgress.objects.filter(pk=instance.pk).update(updated_at=updated_at)

        update_payload = {
            "habit": self.habits[0].id,
            "status": "fail",
        }

        self._test_update_habit_progress_success(update_payload)

    def test_cannot_update_habit_progress_fail_to_success_status_after_5_minutes(self):
        """Test that habit progress cannot be updated from fail to success status after 5 minutes."""
        self.client.force_authenticate(self.member)

        # last updated - 10 minutes ago
        updated_at = timezone.now() - timedelta(minutes=10)
        instance = HabitProgressFailFactory(user=self.member, habit=self.habits[0])
        HabitProgress.objects.filter(pk=instance.pk).update(updated_at=updated_at)

        update_payload = {
            "habit": self.habits[0].id,
            "status": "success",
        }

        response = self.client.post(self.url, update_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=habit_progress_list_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")

    def _assert_detail_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=habit_progress_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
