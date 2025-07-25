from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from friends.models import FriendsRelation
from friends.serializers import (
    SendFriendshipRequestSerializer,
    AcceptFriendshipRequestSerializer,
    RejectFriendshipRequestSerializer,
    UserConnectionSerializer,
)
from friends.services.friendship import FriendshipService


class SendFriendshipRequestView(generics.CreateAPIView):
    serializer_class = SendFriendshipRequestSerializer


class CancelFriendshipRequestView(APIView):
    queryset = FriendsRelation.objects.all()

    def delete(self, request, user_id):
        from_user = request.user

        FriendshipService.cancel_request(from_user, user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcceptFriendshipRequestView(APIView):
    serializer_class = AcceptFriendshipRequestSerializer

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
    serializer_class = RejectFriendshipRequestSerializer

    def patch(self, request, user_id):
        serializer = RejectFriendshipRequestSerializer(
            data={"from_user_id": user_id}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            RejectFriendshipRequestSerializer(result).data, status=status.HTTP_200_OK
        )


class IncomingFriendshipRequestsView(ListAPIView):
    serializer_class = UserConnectionSerializer

    def get_queryset(self):
        return FriendshipService.get_incoming_requests(self.request.user)


class OutgoingFriendshipRequestsView(ListAPIView):
    serializer_class = UserConnectionSerializer

    def get_queryset(self):
        return FriendshipService.get_outgoing_requests(self.request.user)


class FriendsListView(ListAPIView):
    serializer_class = UserConnectionSerializer

    def get_queryset(self):
        return FriendshipService.get_friends(self.request.user)


class RemoveFriendView(APIView):
    queryset = FriendsRelation.objects.all()

    def delete(self, request, user_id):
        FriendshipService.remove_friend(request.user, user_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
