import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from friends.models import FriendsRelation
from friends.tests.factories.friends_relation import (
    SendFriendshipRequestPayloadFactory,
    FriendsRelationFactory,
)

friends_relation_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "from_user": {"type": "integer"},
        "to_user": {"type": "integer"},
        "status": {"type": "string", "enum": ["pending", "accepted", "rejected"]},
    },
    "required": ["id", "from_user", "to_user", "status"],
    "additionalProperties": False,
}


class SendFriendshipRequestTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory()
        cls.user2 = MemberFactory()

        cls.url = reverse("send-friendship-request")

    def test_send_friendship_request_authentication_required(self):
        """Test that authentication is required for sending friendship request."""
        payload = SendFriendshipRequestPayloadFactory(to_user=self.user2)
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_friendship_request_success(self):
        """Test that a friendship request is sent successfully."""
        self.client.force_authenticate(user=self.user1)

        payload = SendFriendshipRequestPayloadFactory(to_user=self.user2.id)
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            FriendsRelation.objects.filter(
                from_user=self.user1, to_user=self.user2
            ).exists()
        )

        friends_relation = FriendsRelation.objects.filter(
            from_user=self.user1, to_user=self.user2
        ).first()

        self.assertEqual(friends_relation.from_user, self.user1)
        self.assertEqual(friends_relation.to_user.id, payload["to_user"])
        self.assertEqual(friends_relation.status, FriendsRelation.Status.PENDING)

        self._assert_detail_response_schema(response.data)

    def test_cannot_send_friendship_request_to_yourself(self):
        """Test that cannot send friendship request to yourself."""
        self.client.force_authenticate(user=self.user1)

        payload = SendFriendshipRequestPayloadFactory(to_user=self.user1)
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_send_duplicate_friendship_request(self):
        """Test cannot send friendship request if already exists."""
        # create request
        FriendsRelationFactory(from_user=self.user1, to_user=self.user2)

        self.client.force_authenticate(user=self.user1)

        payload = SendFriendshipRequestPayloadFactory(to_user=self.user2)
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_send_friendship_request_if_already_sent(self):
        """Test cannot send friendship request if already sent."""
        FriendsRelationFactory(from_user=self.user1, to_user=self.user2)

        self.client.force_authenticate(user=self.user2)
        payload = SendFriendshipRequestPayloadFactory(to_user=self.user1)
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_send_friendship_request_without_to_user(self):
        """Test cannot send friendship request without to_user field."""
        self.client.force_authenticate(user=self.user1)

        payload = SendFriendshipRequestPayloadFactory()
        payload.pop("to_user")

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _assert_detail_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=friends_relation_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
