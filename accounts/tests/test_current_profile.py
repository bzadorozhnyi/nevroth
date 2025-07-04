import jsonschema

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory

user_profile_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "selected_habits": {"type": "boolean"},
        "full_name": {"type": "string"},
        "role": {"type": "string", "enum": ["member", "admin"]},
    },
    "required": ["id", "email", "selected_habits", "full_name", "role"],
    "additionalProperties": False,
}


class CurrentProfileTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("user-profile")
        cls.user = MemberFactory()

    def test_authentication_required(self):
        """Test that authentication is required."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_current_profile(self):
        """Test that retrieving a current profile works."""
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_response_schema(response.data)

    def test_update_profile_success(self):
        """Test that updating a current profile works."""
        self.client.force_authenticate(self.user)
        updated_payload = {
            "email": "new_email@email.com",
            "full_name": "new_full_name",
        }

        response = self.client.patch(self.url, data=updated_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, updated_payload["email"])
        self.assertEqual(self.user.full_name, updated_payload["full_name"])
        self.assertEqual(self.user.role, "member")  # Must remain the same

        self._assert_response_schema(response.data)

    def test_cannot_update_profile_with_empty_email(self):
        """Test that cannot update a profile with an empty email."""
        self.client.force_authenticate(self.user)
        updated_payload = {
            "email": "",
            "full_name": "new_full_name",
        }

        response = self.client.post(self.url, updated_payload)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_update_profile_with_empty_name(self):
        """Test that cannot update a profile with an empty name."""
        self.client.force_authenticate(self.user)
        updated_payload = {
            "email": "new_email@email.com",
            "full_name": "",
        }

        response = self.client.post(self.url, updated_payload)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_update_role(self):
        """Test that cannot update role through profile updating."""
        self.client.force_authenticate(self.user)
        updated_payload = {
            "role": "admin",
        }

        response = self.client.patch(self.url, data=updated_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.data)

    def _assert_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=user_profile_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
