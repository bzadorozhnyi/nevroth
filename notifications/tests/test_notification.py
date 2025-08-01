from collections import Counter

import jsonschema
import random

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.settings import api_settings

from accounts.tests.factories.user import MemberFactory, AdminFactory
from habits.models import Habit
from habits.tests.factories.habit import HabitFactory, UserHabitFactory
from notifications.models import Notification
from notifications.tests.factories.notification import (
    NotificationFactory,
    NotificationCreateForUserPayloadFactory,
    NotificationCreateByHabitsPayloadFactory,
)

notification_message_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "sender": {"type": "integer"},
        "image_url": {
            "type": ["string", "null"],
            "format": "uri",
        },
        "text": {
            "type": "string",
            "maxLength": 300,
        },
    },
    "required": ["id", "sender", "text"],
    "additionalProperties": False,
}

notification_detail_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "recipient": {"type": "integer"},
        "message": notification_message_schema,
        "is_read": {"type": "boolean"},
        "sent_at": {
            "type": "string",
            "format": "date-time",
        },
    },
    "required": ["id", "recipient", "message", "is_read", "sent_at"],
    "additionalProperties": False,
}

notification_list_schema = {
    "type": "array",
    "items": notification_detail_schema,
}

create_notifications_by_habits_response_schema = {
    "type": "object",
    "properties": {
        "created": {
            "type": "integer",
            "description": "Number of notifications successfully created",
        },
        "skipped": {
            "type": "integer",
            "description": "Number of invalid or ignored habit IDs",
        },
        "invalid_habits_ids": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "List of habit IDs that were invalid or not found",
        },
        "message": {
            "type": "string",
            "description": "Human-readable summary of the result",
        },
    },
    "required": ["created", "skipped", "invalid_habits_ids", "message"],
    "additionalProperties": False,
}


class NotificationTestS(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.admin = AdminFactory()

        # Remove default habits
        Habit.objects.all().delete()
        cls.habits = HabitFactory.create_batch(5)

        member_notifications = NotificationFactory.create_batch(5, recipient=cls.member)
        admin_notifications = NotificationFactory.create_batch(5, recipient=cls.admin)
        cls.notifications = member_notifications + admin_notifications
        random.shuffle(cls.notifications)

        cls.list_url = reverse("notification-list")
        cls.detail_url = "notification-detail"
        cls.create_notification_for_user = reverse(
            "notification-create_notification_for_user"
        )
        cls.create_notifications_by_habits = reverse(
            "notification-create_notifications_by_habits"
        )
        cls.mark_as_read = "notification-mark_as_read"

    def test_list_notifications_authentication_required(self):
        """Test that authentication is required to list notifications."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_as_authenticated_user(self):
        """Test that authenticated user can list notifications."""
        users = [self.member, self.admin]

        for user in users:
            with self.subTest(f"user {user}"):
                self.client.force_authenticate(user)
                response = self.client.get(self.list_url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.data
                results = data["results"]

                expected_total_count = Notification.objects.filter(
                    recipient=user
                ).count()
                self.assertEqual(data["count"], expected_total_count)
                expected_page_size = api_settings.DEFAULT_PAGINATION_CLASS.page_size
                self.assertLessEqual(len(results), expected_page_size)

                self.assertTrue(len(results) > 0)
                self._assert_list_response_schema(results)

    def test_retrieve_notification_authentication_required(self):
        """Test that authentication is required to retrieve notification."""
        url = reverse(self.detail_url, kwargs={"pk": self.notifications[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_notification_as_authenticated_user(self):
        """Test that authenticated user can retrieve notification."""
        users = [self.member, self.admin]
        for user in users:
            with self.subTest(f"retrieve notification {user}"):
                self.client.force_authenticate(user)

                # create notification for user
                notification = NotificationFactory(recipient=user)

                url = reverse(self.detail_url, kwargs={"pk": notification.pk})
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                result = response.data
                self.assertEqual(result["id"], notification.id)
                self.assertEqual(result["recipient"], notification.recipient.id)
                self.assertEqual(result["message"]["id"], notification.message.id)
                self.assertEqual(
                    result["message"]["image_url"], notification.message.image_url
                )
                self.assertFalse(result["is_read"])

                self._assert_detail_response_schema(result)

    def test_create_notification_for_user_authentication_required(self):
        """Test that authentication is required to create notification."""
        payload = NotificationCreateForUserPayloadFactory()
        response = self.client.post(self.create_notification_for_user, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_create_notification_for_user_as_member(self):
        """Test that member cannot create notification for user."""
        self.client.force_authenticate(self.member)
        payload = NotificationCreateForUserPayloadFactory()
        response = self.client.post(self.create_notification_for_user, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_notification_for_user_as_admin(self):
        """Test that admin can create notification for user."""
        self.client.force_authenticate(self.admin)
        payload = NotificationCreateForUserPayloadFactory(recipient=self.member.id)
        response = self.client.post(self.create_notification_for_user, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.member.id, message__text=payload["text"]
            ).exists()
        )

        notification = Notification.objects.get(
            recipient=self.member.id, message__text=payload["text"]
        )

        self.assertEqual(notification.recipient, self.member)
        self.assertEqual(notification.message.text, payload["text"])
        self.assertFalse(notification.is_read)

        # Verify response schema
        self._assert_detail_response_schema(response.data)

    def test_can_create_notification_for_user_without_image_url(self):
        """Test that admin can create notification for user without image url."""
        self.client.force_authenticate(self.admin)

        payload = NotificationCreateForUserPayloadFactory(recipient=self.member.id)
        payload.pop("image_url")

        response = self.client.post(self.create_notification_for_user, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.member.id, message__text=payload["text"]
            ).exists()
        )

        notification = Notification.objects.get(
            recipient=self.member.id, message__text=payload["text"]
        )

        self.assertEqual(notification.recipient, self.member)
        self.assertEqual(notification.message.text, payload["text"])
        self.assertFalse(notification.is_read)

        # Verify response schema
        self._assert_detail_response_schema(response.data)

    def test_cannot_create_notification_for_user_without_text(self):
        """Test that notification for user cannot be created without text."""
        self.client.force_authenticate(self.admin)

        payload = NotificationCreateForUserPayloadFactory()
        payload.pop("text")

        response = self.client.post(self.create_notification_for_user, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_notification_for_user_without_recipient(self):
        """Test that notification for user cannot be created without recipient."""
        self.client.force_authenticate(self.admin)

        payload = NotificationCreateForUserPayloadFactory()
        payload.pop("recipient")

        response = self.client.post(self.create_notification_for_user, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_notification_for_user_with_empty_text(self):
        """Test that notification for user cannot be created with empty text."""
        self.client.force_authenticate(self.admin)

        payload = NotificationCreateForUserPayloadFactory(text="")

        response = self.client.post(self.create_notification_for_user, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_notifications_by_habits_authentication_required(self):
        """Test that authentication is required to create notification by habits."""
        payload = NotificationCreateByHabitsPayloadFactory()
        response = self.client.post(
            self.create_notifications_by_habits, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_create_notifications_by_habits_as_member(self):
        """Test that member cannot create notification by habits."""
        self.client.force_authenticate(self.member)
        payload = NotificationCreateByHabitsPayloadFactory()
        response = self.client.post(
            self.create_notifications_by_habits, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_notifications_by_habits_as_admin(self):
        """Test that admin can create notification by habits."""
        self.client.force_authenticate(self.admin)

        # remove previous notifications
        Notification.objects.all().delete()

        # select habits for users
        user_habits = [
            (self.member, self.habits[0]),
            (self.member, self.habits[1]),
            (self.admin, self.habits[1]),
        ]
        for user, habit in user_habits:
            UserHabitFactory(user=user, habit=habit)

        # Duplicate IDs to verify that notifications are not created multiple times for the same habit
        duplicated_ids = [habit.id for (_, habit) in user_habits] * 2

        # Include an invalid ID to ensure the endpoint handles it gracefully without failing
        invalid_habit_id = 12345678
        invalid_ids = [invalid_habit_id]

        # Combine both
        habits_ids = duplicated_ids + invalid_ids

        payload = NotificationCreateByHabitsPayloadFactory(habits_ids=habits_ids)

        response = self.client.post(
            self.create_notifications_by_habits, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check if notifications' count is correct for users
        expected_notifications_count = Counter(user for (user, habit) in user_habits)
        self.assertEqual(
            Notification.objects.filter(recipient=self.member).count(),
            expected_notifications_count[self.member],
        )
        self.assertEqual(
            Notification.objects.filter(recipient=self.admin).count(),
            expected_notifications_count[self.admin],
        )

        result = response.data

        self.assertEqual(result["created"], len(set(user_habits)))
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(result["invalid_habits_ids"], [invalid_habit_id])

        self._assert_create_notifications_by_habits_response_schema(result)

    def test_cannot_create_notifications_by_habits_without_text(self):
        """Test that notifications by habit cannot be created without text."""
        self.client.force_authenticate(self.admin)

        payload = NotificationCreateByHabitsPayloadFactory()
        payload.pop("text")

        response = self.client.post(
            self.create_notifications_by_habits, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_notifications_by_habits_without_habits(self):
        """Test that notifications by habit cannot be created without habits."""
        self.client.force_authenticate(self.admin)

        payload = NotificationCreateByHabitsPayloadFactory()
        payload.pop("habits_ids")

        response = self.client.post(
            self.create_notifications_by_habits, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_notifications_by_habits_with_empty_text(self):
        """Test that notifications by habit cannot be created with empty text."""
        self.client.force_authenticate(self.admin)

        payload = NotificationCreateByHabitsPayloadFactory(text="")

        response = self.client.post(
            self.create_notifications_by_habits, payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mark_as_read_authentication_required(self):
        """Test that authentication is required to mark notification as read."""
        notification = NotificationFactory()
        url = reverse(self.mark_as_read, kwargs={"pk": notification.id})

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_as_read_as_authenticated_user(self):
        """Test that authenticated user can mark notification as read."""

        users = [self.member, self.admin]
        for user in users:
            with self.subTest(f"mark as read for {user}"):
                self.client.force_authenticate(user)
                # create notification for user
                notification = NotificationFactory(recipient=user)

                url = reverse(self.mark_as_read, kwargs={"pk": notification.id})

                response = self.client.patch(url)
                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_notification_authentication_required(self):
        """Test that authentication is required to delete notifications."""
        notification = NotificationFactory()

        url = reverse(self.detail_url, kwargs={"pk": notification.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_notification_as_authenticated_user(self):
        """Test that authenticated user can delete notifications."""
        users = [self.member, self.admin]

        for user in users:
            with self.subTest(f"delete for {user}"):
                self.client.force_authenticate(user)

                # create notification for user
                notification = NotificationFactory(recipient=user)
                url = reverse(self.detail_url, kwargs={"pk": notification.id})
                response = self.client.delete(url)

                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=notification_list_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")

    def _assert_detail_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=notification_detail_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")

    def _assert_create_notifications_by_habits_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(
                instance=data, schema=create_notifications_by_habits_response_schema
            )
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
