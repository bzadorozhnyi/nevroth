from rest_framework.test import APITestCase

from friends.tests.factories.friends_relation import (
    FriendsRelationFactory,
    FriendsRelationPendingFactory,
    FriendsRelationAcceptedFactory,
    FriendsRelationRejectedFactory,
    SendFriendshipRequestPayloadFactory,
)


class TestFactories(APITestCase):
    def test_friends_relation_factories(self):
        FriendsRelationFactory()
        FriendsRelationPendingFactory()
        FriendsRelationAcceptedFactory()
        FriendsRelationRejectedFactory()

    def test_send_friendship_request_factory(self):
        SendFriendshipRequestPayloadFactory()
