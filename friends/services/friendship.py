from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from friends.models import FriendsRelation

User = get_user_model()


class FriendshipService:
    @classmethod
    def is_relation_exist(cls, from_user: User, to_user: User) -> bool:
        return FriendsRelation.objects.filter(
            Q(from_user=from_user, to_user=to_user)
            | Q(from_user=to_user, to_user=from_user)
        ).exists()

    @classmethod
    def ensure_not_self_request(cls, from_user: User, to_user: User):
        if from_user == to_user:
            raise ValidationError(_("You cannot send a friend request to yourself."))

    @classmethod
    def _validate_send_request(cls, from_user: User, to_user: User):
        cls.ensure_not_self_request(from_user, to_user)

        if cls.is_relation_exist(from_user, to_user):
            raise ValidationError(_("Friend request already exists."))

    @classmethod
    def create_send_request(cls, from_user: User, to_user: User) -> FriendsRelation:
        cls._validate_send_request(from_user, to_user)
        return FriendsRelation.objects.create(from_user=from_user, to_user=to_user)

    @classmethod
    def _validate_cancel_request(cls, relation: FriendsRelation):
        if not relation:
            raise PermissionDenied(_("No pending friend request found."))

        if relation.status != FriendsRelation.Status.PENDING:
            raise ValidationError(_("Only pending requests can be cancelled."))

    @classmethod
    def cancel_request(cls, from_user: User, to_user_id: int):
        relation = FriendsRelation.objects.filter(
            from_user=from_user, to_user__id=to_user_id
        ).first()

        cls._validate_cancel_request(relation)

        relation.delete()

    @classmethod
    def _validate_change_status(cls, relation: FriendsRelation):
        if not relation:
            raise NotFound(_("Friend request not found."))

        if relation.status == FriendsRelation.Status.ACCEPTED:
            raise ValidationError(_("Request has been already accepted."))

        if relation.status == FriendsRelation.Status.REJECTED:
            raise ValidationError(_("Request has been already rejected."))

    @classmethod
    def accept_request(cls, from_user_id: int, to_user: User):
        relation = FriendsRelation.objects.filter(
            from_user__id=from_user_id, to_user=to_user
        ).first()

        cls._validate_change_status(relation)

        relation.status = FriendsRelation.Status.ACCEPTED
        relation.save(update_fields=["status"])

        return relation

    @classmethod
    def reject_request(cls, from_user_id: int, to_user: User):
        relation = FriendsRelation.objects.filter(
            from_user__id=from_user_id, to_user=to_user
        ).first()

        cls._validate_change_status(relation)

        relation.status = FriendsRelation.Status.REJECTED
        relation.save(update_fields=["status"])

        return relation

    @classmethod
    def remove_friend(cls, user1: User, user2_id: int):
        relation = FriendsRelation.objects.filter(
            Q(
                from_user=user1,
                to_user__id=user2_id,
                status=FriendsRelation.Status.ACCEPTED,
            )
            | Q(
                from_user__id=user2_id,
                to_user=user1,
                status=FriendsRelation.Status.ACCEPTED,
            )
        ).first()

        if not relation:
            raise ValidationError(_("You are not friends."))

        relation.delete()
