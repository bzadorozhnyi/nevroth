from django.contrib.auth import get_user_model

from rest_framework import serializers

from friends.models import FriendsRelation
from friends.services.friendship import FriendshipService

User = get_user_model()


class SendFriendshipRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = FriendsRelation
        fields = ["id", "from_user", "to_user", "status"]

    def validate(self, data):
        from_user = self.context["request"].user
        to_user = data["to_user"]

        FriendshipService.validate_send_request(from_user, to_user)

        return data

    def create(self, validated_data):
        from_user = self.context["request"].user
        to_user = validated_data["to_user"]

        request = FriendshipService.create_send_request(from_user, to_user)

        return request


class CancelFriendshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendsRelation
        fields = ["id"]


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
