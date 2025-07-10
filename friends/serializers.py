from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from friends.models import FriendsRelation
from friends.services.friendship import FriendshipService

User = get_user_model()


class SendFriendshipRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = FriendsRelation
        fields = ["to_user", "status"]

    def create(self, validated_data):
        from_user = self.context["request"].user
        to_user = validated_data["to_user"]

        return FriendshipService.create_send_request(from_user, to_user)


class AcceptFriendshipRequestSerializer(serializers.Serializer):
    from_user_id = serializers.IntegerField(required=True, write_only=True)
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)

    def save(self):
        to_user = self.context["request"].user
        from_user_id = self.validated_data["from_user_id"]

        return FriendshipService.accept_request(from_user_id, to_user)


class RejectFriendshipRequestSerializer(serializers.Serializer):
    from_user_id = serializers.IntegerField(required=True, write_only=True)
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)

    def save(self):
        to_user = self.context["request"].user
        from_user_id = self.validated_data["from_user_id"]

        return FriendshipService.reject_request(from_user_id, to_user)


class RemoveFriendSerializer(serializers.Serializer):
    friend_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )

    def validate_friend_id(self, friend):
        user = self.context["request"].user
        if not FriendshipService.are_friends(user, friend):
            raise serializers.ValidationError(_("You are not friends."))

        return friend
