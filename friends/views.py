from rest_framework import generics

from friends.models import FriendsRelation
from friends.serializers import (
    SendFriendshipRequestSerializer,
    CancelFriendshipRequestSerializer,
)


class SendFriendshipRequestView(generics.CreateAPIView):
    serializer_class = SendFriendshipRequestSerializer


class CancelFriendshipRequestView(generics.DestroyAPIView):
    serializer_class = CancelFriendshipRequestSerializer

    def get_queryset(self):
        return FriendsRelation.objects.filter(from_user=self.request.user)
