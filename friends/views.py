from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from friends.models import FriendsRelation
from friends.serializers import (
    SendFriendshipRequestSerializer,
    CancelFriendshipRequestSerializer,
    AcceptFriendshipRequestSerializer,
    RejectFriendshipRequestSerializer,
    RemoveFriendSerializer,
)
from friends.services.friendship import FriendshipService


class SendFriendshipRequestView(generics.CreateAPIView):
    serializer_class = SendFriendshipRequestSerializer


class CancelFriendshipRequestView(generics.DestroyAPIView):
    queryset = FriendsRelation.objects.all()
    serializer_class = CancelFriendshipRequestSerializer

    def perform_destroy(self, instance):
        FriendshipService.validate_cancel_request(instance, self.request.user)
        FriendshipService.cancel_request(instance)


class AcceptFriendshipRequestView(generics.UpdateAPIView):
    queryset = FriendsRelation.objects.all()
    serializer_class = AcceptFriendshipRequestSerializer


class RejectFriendshipRequestView(generics.UpdateAPIView):
    queryset = FriendsRelation.objects.all()
    serializer_class = RejectFriendshipRequestSerializer


class RemoveFriendView(APIView):
    queryset = FriendsRelation.objects.all()

    def delete(self, request):
        serializer = RemoveFriendSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        FriendshipService.remove_friend(
            request.user, serializer.validated_data["friend_id"]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
