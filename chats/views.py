from rest_framework import generics, mixins, viewsets

from chats.serializers import (
    ChatSerializer,
    PrivateChatSerializer,
    ChatMessageCreateSerializer,
    ChatMessageUpdateSerializer,
)
from chats.services.chat import ChatService
from chats.models import Chat, ChatMessage
from chats.services.chat_message import ChatMessageService


class ChatListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return ChatSerializer

        return PrivateChatSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Chat.objects.none()

        return ChatService.get_user_chats(self.request.user)


class ChatMessageView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ChatMessage.objects.none()

        return ChatMessage.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return ChatMessageCreateSerializer

        return ChatMessageUpdateSerializer

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        ChatMessageService.ensure_user_is_owner(message, request.user)
        return super().destroy(request, *args, **kwargs)
