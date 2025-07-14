import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from friends.models import FriendsRelation
from friends.tests.factories.friends_relation import (
    FriendsRelationFactory,
)

friends_list_response_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "full_name": {"type": "string"},
        },
        "required": ["id", "full_name"],
        "additionalProperties": False,
    },
}


class FriendsListTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory()
        cls.user2 = MemberFactory()
        cls.user3 = MemberFactory()

        cls.url = reverse("friends-list")

    def test_list_friends_authentication_required(self):
        """Test that authentication is required to list friends."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def format_relations(self, relations):
        return " & ".join(
            f"{from_user} → {to_user} [{status}]"
            for from_user, to_user, status in relations
        )

    def test_list_friends_success(self):
        """Test that friends are listed successfully."""
        self.client.force_authenticate(user=self.user1)

        relation_test_cases = [
            [(self.user1, self.user2, FriendsRelation.Status.PENDING)],
            [(self.user1, self.user2, FriendsRelation.Status.ACCEPTED)],
            [(self.user1, self.user2, FriendsRelation.Status.REJECTED)],
            [
                (self.user1, self.user2, FriendsRelation.Status.ACCEPTED),
                (self.user3, self.user1, FriendsRelation.Status.ACCEPTED),
            ],
            [
                (self.user1, self.user2, FriendsRelation.Status.ACCEPTED),
                (self.user1, self.user3, FriendsRelation.Status.ACCEPTED),
            ],
            [
                (self.user1, self.user2, FriendsRelation.Status.REJECTED),
                (self.user3, self.user1, FriendsRelation.Status.ACCEPTED),
            ],
            [
                (self.user1, self.user2, FriendsRelation.Status.PENDING),
                (self.user3, self.user1, FriendsRelation.Status.PENDING),
            ],
        ]

        for relations in relation_test_cases:
            with self.subTest(self.format_relations(relations)):
                # Remove previous relations
                FriendsRelation.objects.all().delete()

                # Create new relations
                for user1, user2, relation_status in relations:
                    FriendsRelationFactory(
                        from_user=user1, to_user=user2, status=relation_status
                    )

                response = self.client.get(self.url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.data

                # get friends of self.user1
                accepted_users = [
                    user.id
                    for (user1, user2, status) in relations
                    for user in (user1, user2)
                    if status == FriendsRelation.Status.ACCEPTED and user != self.user1
                ]
                response_friends = [friend["id"] for friend in results]

                self.assertCountEqual(response_friends, accepted_users)
                self._assert_list_response_schema(results)

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=friends_list_response_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
