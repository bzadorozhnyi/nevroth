import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from friends.models import FriendsRelation
from friends.tests.factories.friends_relation import (
    FriendsRelationFactory,
    FriendsRelationAcceptedFactory,
    FriendsRelationPendingFactory,
)

user_connection_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "full_name": {"type": "string"},
    },
    "required": ["id", "full_name"],
    "additionalProperties": False,
}

friendship_statuses_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"]},
        "previous": {"type": ["string", "null"]},
        "results": {
            "type": "array",
            "items": user_connection_schema,
        },
    },
    "required": ["count", "next", "previous", "results"],
    "additionalProperties": False,
}


class FriendshipStatusesTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory()
        cls.user2 = MemberFactory()
        cls.user3 = MemberFactory()

        cls.relation_test_cases = [
            [(cls.user1, cls.user2, FriendsRelation.Status.PENDING)],
            [(cls.user1, cls.user2, FriendsRelation.Status.ACCEPTED)],
            [(cls.user1, cls.user2, FriendsRelation.Status.REJECTED)],
            [(cls.user2, cls.user1, FriendsRelation.Status.PENDING)],
            [(cls.user2, cls.user1, FriendsRelation.Status.ACCEPTED)],
            [(cls.user2, cls.user1, FriendsRelation.Status.REJECTED)],
            [
                (cls.user1, cls.user2, FriendsRelation.Status.ACCEPTED),
                (cls.user3, cls.user1, FriendsRelation.Status.ACCEPTED),
            ],
            [
                (cls.user1, cls.user2, FriendsRelation.Status.ACCEPTED),
                (cls.user1, cls.user3, FriendsRelation.Status.ACCEPTED),
            ],
            [
                (cls.user1, cls.user2, FriendsRelation.Status.REJECTED),
                (cls.user3, cls.user1, FriendsRelation.Status.ACCEPTED),
            ],
            [
                (cls.user1, cls.user2, FriendsRelation.Status.PENDING),
                (cls.user3, cls.user1, FriendsRelation.Status.PENDING),
            ],
            [
                (cls.user2, cls.user1, FriendsRelation.Status.PENDING),
                (cls.user3, cls.user1, FriendsRelation.Status.PENDING),
            ],
            [
                (cls.user2, cls.user1, FriendsRelation.Status.PENDING),
                (cls.user3, cls.user1, FriendsRelation.Status.ACCEPTED),
            ],
            [
                (cls.user1, cls.user2, FriendsRelation.Status.PENDING),
                (cls.user3, cls.user1, FriendsRelation.Status.ACCEPTED),
            ],
        ]

        cls.friends_list = reverse("friends-list")
        cls.incoming_requests = reverse("incoming-friend-requests")
        cls.outgoing_requests = reverse("outgoing-friend-requests")

    def format_relations(self, relations):
        return " & ".join(
            f"{from_user} → {to_user} [{status}]"
            for from_user, to_user, status in relations
        )

    def test_list_friends_authentication_required(self):
        """Test that authentication is required to list friends."""
        response = self.client.get(self.friends_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_friends_success(self):
        """Test that friends are listed successfully."""
        self.client.force_authenticate(user=self.user1)

        for relations in self.relation_test_cases:
            with self.subTest(self.format_relations(relations)):
                # Remove previous relations
                FriendsRelation.objects.all().delete()

                # Create new relations
                for user1, user2, relation_status in relations:
                    FriendsRelationFactory(
                        from_user=user1, to_user=user2, status=relation_status
                    )

                response = self.client.get(self.friends_list)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.data["results"]

                # get friends of self.user1
                accepted_users = [
                    user.id
                    for (user1, user2, status) in relations
                    for user in (user1, user2)
                    if status == FriendsRelation.Status.ACCEPTED and user != self.user1
                ]
                response_friends = [friend["id"] for friend in results]

                self.assertEqual(response.data["count"], len(accepted_users))
                self.assertIsNone(response.data["next"])
                self.assertIsNone(response.data["previous"])
                self.assertCountEqual(response_friends, accepted_users)
                self._assert_list_response_schema(response.data)

    def test_paginated_list_friends_multiple_pages(self):
        """Test that friends are listed with correct pagination over multiple pages."""
        self.client.force_authenticate(self.user1)

        for _ in range(15):
            other_user = MemberFactory()
            FriendsRelationAcceptedFactory(from_user=self.user1, to_user=other_user)

        # check first page
        response = self.client.get(self.friends_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["count"], 15)
        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

        # check second page
        next_url = data["next"]
        response2 = self.client.get(next_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data2 = response2.data
        self.assertEqual(len(data2["results"]), 5)
        self.assertIsNone(data2["next"])
        self.assertIsNotNone(data2["previous"])

        # Verify response schemas
        self._assert_list_response_schema(data)
        self._assert_list_response_schema(data2)

    def test_list_incoming_friendship_requests_authentication_required(self):
        """Test that authentication is required to list incoming friendship requests."""
        response = self.client.get(self.incoming_requests)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_incoming_friendship_requests_success(self):
        """Test that incoming friendship requests are listed successfully."""
        self.client.force_authenticate(user=self.user1)

        for relations in self.relation_test_cases:
            with self.subTest(self.format_relations(relations)):
                # Remove previous relations
                FriendsRelation.objects.all().delete()

                # Create new relations
                for user1, user2, relation_status in relations:
                    FriendsRelationFactory(
                        from_user=user1, to_user=user2, status=relation_status
                    )

                response = self.client.get(self.incoming_requests)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.data["results"]

                # get incoming friendship requests to self.user1
                incoming_requests = [
                    from_user.id
                    for (from_user, to_user, status) in relations
                    if status == FriendsRelation.Status.PENDING
                    and to_user == self.user1
                ]
                incoming_requests_users = [req["id"] for req in results]

                self.assertEqual(response.data["count"], len(incoming_requests))
                self.assertIsNone(response.data["next"])
                self.assertIsNone(response.data["previous"])
                self.assertCountEqual(incoming_requests_users, incoming_requests)
                self._assert_list_response_schema(response.data)

    def test_paginated_incoming_friendship_requests_multiple_pages(self):
        """Test that incoming friendship requests are listed with correct pagination over multiple pages."""
        self.client.force_authenticate(self.user1)

        for _ in range(15):
            other_user = MemberFactory()
            FriendsRelationPendingFactory(from_user=other_user, to_user=self.user1)

        # check first page
        response = self.client.get(self.incoming_requests)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["count"], 15)
        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

        # check second page
        next_url = data["next"]
        response2 = self.client.get(next_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data2 = response2.data
        self.assertEqual(len(data2["results"]), 5)
        self.assertIsNone(data2["next"])
        self.assertIsNotNone(data2["previous"])

        # Verify response schemas
        self._assert_list_response_schema(data)
        self._assert_list_response_schema(data2)

    def test_list_outgoing_friendship_requests_authentication_required(self):
        """Test that authentication is required to list outgoing friendship requests."""
        response = self.client.get(self.outgoing_requests)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_outgoing_friendship_requests_success(self):
        """Test that outgoing friendship requests are listed successfully."""
        self.client.force_authenticate(user=self.user1)

        for relations in self.relation_test_cases:
            with self.subTest(self.format_relations(relations)):
                # Remove previous relations
                FriendsRelation.objects.all().delete()

                # Create new relations
                for user1, user2, relation_status in relations:
                    FriendsRelationFactory(
                        from_user=user1, to_user=user2, status=relation_status
                    )

                response = self.client.get(self.outgoing_requests)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.data["results"]

                # get outgoing friendship requests from self.user1
                outgoing_requests = [
                    to_user.id
                    for (from_user, to_user, status) in relations
                    if status == FriendsRelation.Status.PENDING
                    and from_user == self.user1
                ]
                outgoing_requests_users = [req["id"] for req in results]

                self.assertEqual(response.data["count"], len(outgoing_requests))
                self.assertIsNone(response.data["next"])
                self.assertIsNone(response.data["previous"])
                self.assertCountEqual(outgoing_requests_users, outgoing_requests)
                self._assert_list_response_schema(response.data)

    def test_paginated_outgoing_friendship_requests_multiple_pages(self):
        """Test that outgoing friendship requests are listed with correct pagination over multiple pages."""
        self.client.force_authenticate(self.user1)

        for _ in range(15):
            other_user = MemberFactory()
            FriendsRelationPendingFactory(from_user=self.user1, to_user=other_user)

        # check first page
        response = self.client.get(self.outgoing_requests)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["count"], 15)
        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

        # check second page
        next_url = data["next"]
        response2 = self.client.get(next_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data2 = response2.data
        self.assertEqual(len(data2["results"]), 5)
        self.assertIsNone(data2["next"])
        self.assertIsNotNone(data2["previous"])

        # Verify response schemas
        self._assert_list_response_schema(data)
        self._assert_list_response_schema(data2)

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(
                instance=data, schema=friendship_statuses_list_response_schema
            )
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
