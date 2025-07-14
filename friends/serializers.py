from django.contrib.auth import get_user_model

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


class UserConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name"]
