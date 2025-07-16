from rest_framework.generics import ListAPIView

from chats.serializers import ChatSerializer
from chats.services.chat import ChatService


class ChatListView(ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        return ChatService.get_chats_for_user(self.request.user)
