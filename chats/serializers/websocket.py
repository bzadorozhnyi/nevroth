from rest_framework import serializers

from chats.models import ChatMessage
from chats.serializers.sender import ChatMessageSenderSerializer


class ChatMessageForWebsocketSerializer(serializers.ModelSerializer):
    sender = ChatMessageSenderSerializer()

    class Meta:
        model = ChatMessage
        fields = ["id", "content", "sender"]


class NewMessageForWebsocketSerializer(serializers.ModelSerializer):
    sender = ChatMessageSenderSerializer()

    class Meta:
        model = ChatMessage
        fields = ["id", "chat", "content", "sender"]
