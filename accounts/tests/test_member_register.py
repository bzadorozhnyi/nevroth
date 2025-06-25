from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from accounts.tests.factories.user import MemberCreatePayloadFactory, MemberFactory


class MemberRegistrationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse("register")

    def test_member_can_register(self):
        """Verify that member can register with valid data."""

        payload = MemberCreatePayloadFactory()

        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(email=payload["email"]).exists())

        user = User.objects.get(email=payload["email"])
        self.assertEqual(user.full_name, payload["full_name"])
        self.assertEqual(user.role, User.Role.MEMBER)

    def test_cannot_register_with_existing_email(self):
        """Verify that member cannot register with an existing email."""

        existing_member = MemberFactory()

        payload = MemberCreatePayloadFactory(email=existing_member.email)

        response = self.client.post(self.register_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.filter(email=existing_member).count(), 1)

    def test_registration_with_missing_required_field(self):
        """Verify that member cannot register with missing required field."""

        payload = {
            "password": "just_password_123",
        }

        response = self.client.post(self.register_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("full_name", response.data)
