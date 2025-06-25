from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory


class VerifyTokenTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.token_obtain_pair = reverse("token_obtain_pair")

    def test_sign_in_member(self):
        member = MemberFactory()

        data = {
            "email": member.email,
            "password": "password"
        }

        response = self.client.post(self.token_obtain_pair, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)