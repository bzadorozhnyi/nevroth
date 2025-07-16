from rest_framework.generics import ListCreateAPIView

from chats.serializers import ChatSerializer, PrivateChatSerializer
from chats.services.chat import ChatService
from chats.models import Chat


class ChatListCreateView(ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return ChatSerializer

        return PrivateChatSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Chat.objects.none()

        return ChatService.get_chats_for_user(self.request.user)
