from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from chats.models import Chat, ChatMessage
from chats.services.chat import ChatService
from chats.services.chat_message import ChatMessageService

User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ["id", "chat_type"]


class PrivateChatSerializer(serializers.ModelSerializer):
    member = serializers.IntegerField(write_only=True)

    class Meta:
        model = Chat
        fields = ["id", "chat_type", "member"]

    def validate_chat_type(self, value):
        if value != "private":
            raise serializers.ValidationError(_("Chat type must be 'private'"))

        return value

    def create(self, validated_data):
        user = self.context["request"].user
        other_user_id = validated_data["member"]

        return ChatService.get_or_create_chat_between(user, other_user_id)


class ChatMessageSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = ChatMessageSenderSerializer()

    class Meta:
        model = ChatMessage
        fields = ["id", "content", "sender"]


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "content", "chat"]

    def create(self, validated_data):
        sender = self.context["request"].user
        content = validated_data["content"]
        chat = validated_data["chat"]

        return ChatMessageService.create_message(sender, chat, content)


class ChatMessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "content", "chat"]
        read_only_fields = ["id", "chat"]

    def update(self, instance, validated_data):
        instance.content = validated_data["content"]
        instance.save(update_fields=["content"])

        return instance
