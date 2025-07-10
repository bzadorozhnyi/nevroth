from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from friends.models import FriendsRelation
from friends.serializers import (
    SendFriendshipRequestSerializer,
    AcceptFriendshipRequestSerializer,
    RejectFriendshipRequestSerializer,
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


class AcceptFriendshipRequestView(APIView):
    def patch(self, request, user_id):
        serializer = AcceptFriendshipRequestSerializer(
            data={"from_user_id": user_id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            AcceptFriendshipRequestSerializer(result).data, status=status.HTTP_200_OK
        )


class RejectFriendshipRequestView(APIView):
    def patch(self, request, user_id):
        serializer = RejectFriendshipRequestSerializer(
            data={"from_user_id": user_id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            RejectFriendshipRequestSerializer(result).data, status=status.HTTP_200_OK
        )


class RemoveFriendView(APIView):
    queryset = FriendsRelation.objects.all()

    def delete(self, request, user_id):
        FriendshipService.remove_friend(request.user, user_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
