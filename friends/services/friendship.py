from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from friends.models import FriendsRelation


class FriendshipService:
    @classmethod
    def is_request_exist(cls, from_user, to_user) -> bool:
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

        if cls.is_request_exist(from_user, to_user):
            raise ValidationError(_("Friend request already exists."))

    @classmethod
    def create_send_request(cls, from_user, to_user) -> FriendsRelation:
        return FriendsRelation.objects.create(from_user=from_user, to_user=to_user)
