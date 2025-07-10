import jsonschema

from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from accounts.tests.factories.user import MemberFactory
from friends.models import FriendsRelation
from friends.tests.factories.friends_relation import (
    FriendsRelationPendingFactory,
    FriendsRelationAcceptedFactory,
    FriendsRelationRejectedFactory,
)

accept_request_response_schema = {
    "type": "object",
    "properties": {
        "from_user": {"type": "integer"},
        "status": {"type": "string", "enum": ["pending", "accepted", "rejected"]},
    },
    "required": ["from_user", "status"],
    "additionalProperties": False,
}


class AcceptFriendshipRequestTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory()
        cls.user2 = MemberFactory()
        cls.user3 = MemberFactory()

        cls.url = "accept-friendship-request"

    def test_accept_friendship_request_authentication_required(self):
        """Test that authentication is required for accepting friendship requests."""
        friends_relation = FriendsRelationPendingFactory()
        url = reverse(self.url, kwargs={"user_id": friends_relation.from_user.id})

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accept_friendship_request_success(self):
        """Test that accepting friendship requests are successful."""
        friends_relation = FriendsRelationPendingFactory(
            from_user=self.user1, to_user=self.user2
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse(self.url, kwargs={"user_id": friends_relation.from_user.id})

        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            FriendsRelation.objects.filter(
                from_user=self.user1,
                to_user=self.user2,
            ).exists()
        )

        friends_relation = FriendsRelation.objects.filter(
            from_user=self.user1,
            to_user=self.user2,
        ).first()

        self.assertEqual(friends_relation.status, FriendsRelation.Status.ACCEPTED)

        self._assert_detail_response_schema(response.data)

    def test_cannot_accept_already_accepted_friendship_request(self):
        """Test that cannot accept a friendship request which has already been accepted."""
        friends_relation = FriendsRelationAcceptedFactory(
            from_user=self.user1, to_user=self.user2
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse(self.url, kwargs={"user_id": friends_relation.from_user.id})

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_accept_already_rejected_friendship_request(self):
        """Test that cannot accept a friendship request which has already been rejected."""
        friends_relation = FriendsRelationRejectedFactory(
            from_user=self.user1, to_user=self.user2
        )
        self.client.force_authenticate(user=self.user2)

        url = reverse(self.url, kwargs={"user_id": friends_relation.from_user.id})

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _assert_detail_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=accept_request_response_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
