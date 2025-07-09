import factory
from factory.django import DjangoModelFactory

from faker import Faker

from accounts.tests.factories.user import BaseUserFactory
from friends.models import FriendsRelation

faker = Faker()


class FriendsRelationFactory(DjangoModelFactory):
    class Meta:
        model = FriendsRelation

    from_user = factory.SubFactory(BaseUserFactory)
    to_user = factory.SubFactory(BaseUserFactory)


class FriendsRelationPendingFactory(FriendsRelationFactory):
    status = FriendsRelation.Status.PENDING


class FriendsRelationAcceptedFactory(FriendsRelationFactory):
    status = FriendsRelation.Status.ACCEPTED


class FriendsRelationRejectedFactory(FriendsRelationFactory):
    status = FriendsRelation.Status.REJECTED


class SendFriendshipRequestPayloadFactory(factory.Factory):
    class Meta:
        model = dict

    to_user = factory.LazyAttribute(lambda o: BaseUserFactory().id)


class RemoveFriendPayloadFactory(factory.Factory):
    class Meta:
        model = dict

    friend_id = factory.LazyAttribute(lambda o: BaseUserFactory().id)
