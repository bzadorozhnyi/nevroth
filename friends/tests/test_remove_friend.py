from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse

from accounts.tests.factories.user import MemberFactory
from friends.models import FriendsRelation
from friends.tests.factories.friends_relation import (
    FriendsRelationAcceptedFactory,
    FriendsRelationPendingFactory,
    FriendsRelationRejectedFactory,
)


class RemoveFriendTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory()
        cls.user2 = MemberFactory()

        cls.url = "remove-friend"

    def test_remove_friend_authentication_required(self):
        """Test that authentication is required to remove a friend."""
        FriendsRelationAcceptedFactory(from_user=self.user1, to_user=self.user2)

        url = reverse(self.url, kwargs={"user_id": self.user2.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_remove_friend_success(self):
        """Test that friend removed successfully."""
        FriendsRelationAcceptedFactory(from_user=self.user1, to_user=self.user2)

        self.client.force_authenticate(user=self.user1)

        url = reverse(self.url, kwargs={"user_id": self.user2.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            FriendsRelation.objects.filter(
                from_user=self.user1, to_user=self.user2
            ).exists()
        )

    def test_cannot_remove_friend_with_pending_request(self):
        """Test that cannot remove a user from friends with pending friendship request."""
        FriendsRelationPendingFactory(from_user=self.user1, to_user=self.user2)

        self.client.force_authenticate(user=self.user1)

        url = reverse(self.url, kwargs={"user_id": self.user2.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_remove_friend_with_rejected_request(self):
        """Test that cannot remove a user from friends with rejected friendship request."""
        FriendsRelationRejectedFactory(from_user=self.user1, to_user=self.user2)

        self.client.force_authenticate(user=self.user1)

        url = reverse(self.url, kwargs={"user_id": self.user2.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_remove_nonfriend_from_friends(self):
        """Test that a user cannot remove someone who is not a friend"""
        self.client.force_authenticate(user=self.user1)

        url = reverse(self.url, kwargs={"user_id": self.user2.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
