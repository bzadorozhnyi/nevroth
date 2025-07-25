import uuid

from django.urls import reverse
from django.core import mail
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import VerifyToken
from accounts.tests.factories.user import MemberFactory


class ForgotPasswordFlowTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = MemberFactory()
        cls.request_url = reverse("request_forgot_password")
        cls.update_url = reverse("update_forgot_password")

    def test_request_forgot_password_with_unregistered_email(self):
        """Ensure that is the email is not registered, the endpoint returns 204."""
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(self.request_url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_request_forgot_password_success(self):
        """
        Verify that requesting a forgot password for a registered user creates a VerifyToken
        and sends an email.
        """

        settings.CELERY_TASK_ALWAYS_EAGER = True

        data = {"email": self.user.email}
        response = self.client.post(self.request_url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that a VerifyToken was created for this email.
        token = VerifyToken.objects.filter(email=self.user.email).first()
        self.assertIsNotNone(token)

        # Check that an email was sent.
        self.assertGreater(len(mail.outbox), 0)
        sent_email = mail.outbox[-1]
        self.assertIn(self.user.email, sent_email.to)
        self.assertEqual(sent_email.subject, "Nevroth Restore Password")

    def test_update_forgot_password_with_invalid_token(self):
        """Ensure if an invalid token is provided, the endpoint returns an error."""
        data = {
            "token": str(uuid.uuid4()),  # Generates a random UUID that won't match
            "password": "new_secure_password",
        }
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The link is not found", str(response.data))

    def test_update_forgot_password_success(self):
        """Ensure that with a valid token, the password is updated and the VerifyToken is deleted."""
        # Request a forgot password to create a VerifyToken.
        request_data = {"email": self.user.email}
        request_response = self.client.post(self.request_url, request_data)
        self.assertEqual(request_response.status_code, status.HTTP_204_NO_CONTENT)

        token = VerifyToken.objects.filter(email=self.user.email).first()
        self.assertIsNotNone(token)

        new_password = "new_secure_password"
        update_data = {"token": str(token.token), "password": new_password}
        update_response = self.client.post(self.update_url, update_data)
        self.assertEqual(update_response.status_code, status.HTTP_204_NO_CONTENT)

        # After updating, the token should be deleted.
        self.assertFalse(VerifyToken.objects.filter(email=self.user.email).exists())

        # Refresh user from the DB and verify that the password has been updated.
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
