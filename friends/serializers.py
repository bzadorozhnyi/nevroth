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


class AcceptFriendshipRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = FriendsRelation
        fields = ["id", "status"]

    def validate(self, data):
        user = self.context["request"].user
        FriendshipService.validate_accept_request(self.instance.id, user)

        return data

    def update(self, instance, validated_data):
        return FriendshipService.accept_request(instance)


class RejectFriendshipRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = FriendsRelation
        fields = ["id", "status"]

    def validate(self, data):
        user = self.context["request"].user
        FriendshipService.validate_reject_request(self.instance.id, user)

        return data

    def update(self, instance, validated_data):
        return FriendshipService.reject_request(instance)


class RemoveFriendSerializer(serializers.Serializer):
    friend_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )

    def validate_friend_id(self, friend):
        user = self.context["request"].user
        if not FriendshipService.are_friends(user, friend):
            raise serializers.ValidationError(_("You are not friends."))

        return friend
