from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from friends.models import FriendsRelation
from friends.serializers import (
    SendFriendshipRequestSerializer,
    AcceptFriendshipRequestSerializer,
    RejectFriendshipRequestSerializer,
    RemoveFriendSerializer,
)
from friends.services.friendship import FriendshipService


class SendFriendshipRequestView(generics.CreateAPIView):
    serializer_class = SendFriendshipRequestSerializer


class CancelFriendshipRequestView(generics.DestroyAPIView):
    queryset = FriendsRelation.objects.all()

    def delete(self, request, *args, **kwargs):
        from_user = request.user
        to_user_id = kwargs.get("user_id")

        FriendshipService.cancel_request(from_user, to_user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
