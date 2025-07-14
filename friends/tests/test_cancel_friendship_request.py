from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from accounts.tests.factories.user import MemberFactory
from friends.models import FriendsRelation
from friends.tests.factories.friends_relation import (
    FriendsRelationFactory,
    FriendsRelationAcceptedFactory,
    FriendsRelationRejectedFactory,
)


class CancelFriendshipRequestTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory()
        cls.user2 = MemberFactory()
        cls.user3 = MemberFactory()

        cls.friends_relations = [
            FriendsRelationFactory(from_user=cls.user1, to_user=cls.user2)
        ]

        cls.url = "cancel-friendship-request"

    def test_cancel_friendship_request_authentication_required(self):
        """Test that authentication is required to cancel a friendship request"""
        url = reverse(
            self.url, kwargs={"user_id": self.friends_relations[0].to_user.id}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancel_friendship_request_success(self):
        """Test that a friendship request can be cancelled"""
        self.client.force_authenticate(user=self.user1)
        url = reverse(
            self.url, kwargs={"user_id": self.friends_relations[0].to_user.id}
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            FriendsRelation.objects.filter(
                from_user=self.user1, to_user=self.user2
            ).exists()
        )

    def test_cannot_cancel_friendship_request_from_another_user(self):
        """Test that a friendship request cannot be cancelled from another user"""
        self.client.force_authenticate(user=self.user2)
        url = reverse(
            self.url, kwargs={"user_id": self.friends_relations[0].to_user.id}
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_friend_request_between_other_users(self):
        """Test that a friendship request cannot be deleted between others users"""
        self.client.force_authenticate(user=self.user3)
        url = reverse(
            self.url, kwargs={"user_id": self.friends_relations[0].to_user.id}
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_cancel_already_accepted_friendship_request(self):
        """Test that a friendship request cannot be canceled when already accepted"""
        accepted_friends_relation = FriendsRelationAcceptedFactory(
            from_user=self.user1, to_user=self.user3
        )

        self.client.force_authenticate(user=self.user1)

        url = reverse(
            self.url, kwargs={"user_id": accepted_friends_relation.to_user.id}
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_already_rejected_friendship_request(self):
        """Test that a friendship request cannot be canceled when already rejected"""
        rejected_friends_relation = FriendsRelationRejectedFactory(
            from_user=self.user1, to_user=self.user3
        )

        self.client.force_authenticate(user=self.user1)

        url = reverse(
            self.url, kwargs={"user_id": rejected_friends_relation.to_user.id}
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
