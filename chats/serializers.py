from django.contrib.auth import get_user_model
from rest_framework import serializers

from chats.models import Chat

User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ["id", "chat_type"]
