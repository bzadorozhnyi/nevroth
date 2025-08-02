import uuid

import jsonschema

from django.contrib.auth import get_user_model
from django.urls import reverse

from unittest.mock import Mock, patch

from rest_framework.test import APITestCase
from rest_framework import status

from accounts.tests.factories.user import BaseUserFactory, AdminFactory
from notifications.services.s3_service import S3Service

User = get_user_model()

presigned_url_response_schema = {
    "type": "object",
    "properties": {
        "image_path": {"type": "string"},
        "pre_signed_url": {"type": "string"},
    },
    "required": ["image_path", "pre_signed_url"],
    "additionalProperties": False,
}


class NotificationImageUploadViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mock_image_path = "notifications/test.png"
        cls.mock_presigned_url = "https://mock-presigned-url.com"

        cls.mock_generate_url_func = Mock(
            return_value=(cls.mock_image_path, cls.mock_presigned_url)
        )

        cls.url = reverse("notification-presigned-url")

    def test_authentication_required(self):
        """Test that authentication is required."""
        with patch.object(
            S3Service, "generate_presign_url", self.mock_generate_url_func
        ):
            response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_forbidden_for_other_roles(self):
        """Test that only admins can access this endpoint."""
        for case in User.Role.choices:
            if case[0] == User.Role.ADMIN:
                continue

            with self.subTest(case=case):
                user = BaseUserFactory(role=case[0])
                self.client.force_authenticate(user)

                with patch.object(
                    S3Service, "generate_presign_url", self.mock_generate_url_func
                ):
                    response = self.client.post(self.url, {"image_extension": "png"})

                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_success(self):
        """Test that admin can create an image."""
        admin = AdminFactory()
        self.client.force_authenticate(admin)

        data = {
            "image_extension": "png",
            "content_type": "application/png",
        }

        with patch.object(
            S3Service, "generate_presign_url", self.mock_generate_url_func
        ):
            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.mock_generate_url_func.assert_called_once_with(
            image_extension=data["image_extension"],
            content_type=data["content_type"],
        )
        self._assert_response_schema(response.data)

    def test_create_wrong_image_extension(self):
        """Test that invalid image extension raises error."""
        admin = AdminFactory()
        self.client.force_authenticate(admin)

        with patch.object(
            S3Service, "generate_presign_url", self.mock_generate_url_func
        ):
            response = self.client.post(
                self.url,
                {
                    "image_extension": "gif",
                    "content_type": "application/gif",
                },
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is not a valid choice", response.data["image_extension"][0])

    @patch("uuid.uuid4")
    def test_generate_image_path_format(self, mock_uuid4):
        """Test that image path is generated with correct format."""

        mock_uuid = "12345678-1234-5678-1234-567812345678"
        mock_uuid4.return_value = uuid.UUID(mock_uuid)

        image_extension = "png"

        image_path = S3Service._generate_image_path(
            image_extension=image_extension,
        )

        expected_path = f"notifications/{mock_uuid}.{image_extension}"
        self.assertEqual(image_path, expected_path)

    def _assert_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=presigned_url_response_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
