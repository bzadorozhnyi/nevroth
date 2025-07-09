from rest_framework import generics

from friends.serializers import SendFriendshipRequestSerializer


class SendFriendshipRequestView(generics.CreateAPIView):
    serializer_class = SendFriendshipRequestSerializer
