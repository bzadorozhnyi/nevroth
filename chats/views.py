from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response

from chats.models import Chat, ChatMessage
from chats.permissions import IsChatMessageOwner, IsChatMember
from chats.serializers import (
    ChatSerializer,
    PrivateChatSerializer,
    ChatMessageCreateSerializer,
    ChatMessageUpdateSerializer,
    ChatMessageSerializer,
)
from chats.services.chat import ChatService


class ChatListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return ChatSerializer

        return PrivateChatSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Chat.objects.none()

        return ChatService.get_user_chats(self.request.user)


class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsChatMember]

    def get_queryset(self):
        chat_id = self.kwargs.get("id")
        return ChatMessage.objects.filter(chat_id=chat_id).order_by("-created_at")


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

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsChatMember]
        elif self.action in ["update", "destroy"]:
            permission_classes = [IsChatMessageOwner]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return ChatMessageCreateSerializer

        return ChatMessageUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
