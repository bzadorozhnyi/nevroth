from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError, PermissionDenied

from friends.models import FriendsRelation

User = get_user_model()


class FriendshipService:
    @classmethod
    def is_relation_exist(cls, from_user, to_user) -> bool:
        return FriendsRelation.objects.filter(
            Q(from_user=from_user, to_user=to_user)
            | Q(from_user=to_user, to_user=from_user)
        ).exists()

    @classmethod
    def ensure_not_self_request(cls, from_user, to_user):
        if from_user == to_user:
            raise ValidationError(_("You cannot send a friend request to yourself."))

    @classmethod
    def validate_send_request(cls, from_user, to_user):
        cls.ensure_not_self_request(from_user, to_user)

        if cls.is_relation_exist(from_user, to_user):
            raise ValidationError(_("Friend request already exists."))

    @classmethod
    def create_send_request(cls, from_user, to_user) -> FriendsRelation:
        return FriendsRelation.objects.create(from_user=from_user, to_user=to_user)

    @classmethod
    def validate_cancel_request(cls, friends_relation: FriendsRelation, user: User):
        if friends_relation.from_user != user:
            raise PermissionDenied(_("You can only cancel requests you sent."))
        if friends_relation.status != FriendsRelation.Status.PENDING:
            raise ValidationError(_("Only pending requests can be cancelled."))

    @classmethod
    def cancel_request(cls, friends_relation: FriendsRelation):
        friends_relation.delete()

    @classmethod
    @transaction.atomic
    def validate_change_request_status(cls, friends_relation_id: int, user: User):
        if not FriendsRelation.objects.filter(id=friends_relation_id).exists():
            raise ValidationError(_("Friend request does not exist."))

        request = FriendsRelation.objects.filter(id=friends_relation_id).first()

        if request.to_user != user:
            raise PermissionDenied(
                _("You cannot accept friend request which hasn't been sent to you.")
            )

        if request.status == FriendsRelation.Status.ACCEPTED:
            raise ValidationError(_("Friend request already accepted."))
        elif request.status == FriendsRelation.Status.REJECTED:
            raise ValidationError(_("Friend request already rejected."))

    @classmethod
    def update_request_status(
        cls, friends_relation: FriendsRelation, new_status: FriendsRelation.Status
    ) -> FriendsRelation:
        friends_relation.status = new_status
        friends_relation.save(update_fields=["status"])

        return friends_relation

    @classmethod
    def validate_accept_request(cls, friends_relation_id: int, user: User):
        cls.validate_change_request_status(friends_relation_id, user)

    @classmethod
    def accept_request(cls, friends_relation: FriendsRelation) -> FriendsRelation:
        return cls.update_request_status(
            friends_relation, FriendsRelation.Status.ACCEPTED
        )

    @classmethod
    def validate_reject_request(cls, friends_relation_id: int, user: User):
        cls.validate_change_request_status(friends_relation_id, user)

    @classmethod
    def reject_request(cls, friends_relation: FriendsRelation) -> FriendsRelation:
        return cls.update_request_status(
            friends_relation, FriendsRelation.Status.REJECTED
        )

    @classmethod
    def are_friends(cls, user1: User, user2: User) -> bool:
        return FriendsRelation.objects.filter(
            Q(from_user=user1, to_user=user2, status=FriendsRelation.Status.ACCEPTED)
            | Q(from_user=user2, to_user=user1, status=FriendsRelation.Status.ACCEPTED)
        ).exists()

    @classmethod
    @transaction.atomic
    def remove_friend(cls, user1: User, user2: User):
        if not cls.are_friends(user1, user2):
            raise ValidationError(_("You are not friends."))

        relation = FriendsRelation.objects.filter(
            Q(from_user=user1, to_user=user2, status=FriendsRelation.Status.ACCEPTED)
            | Q(from_user=user2, to_user=user1, status=FriendsRelation.Status.ACCEPTED)
        ).first()

        relation.delete()
