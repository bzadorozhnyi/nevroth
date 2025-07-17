from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from chats.models import ChatMember


class IsChatMember(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        chat_id = request.data.get("chat")
        if not chat_id:
            raise ValidationError(_("Chat ID is required"))

        return ChatMember.objects.filter(chat_id=chat_id, user=request.user).exists()


class IsChatMessageOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.sender
