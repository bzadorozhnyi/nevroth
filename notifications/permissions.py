from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

User = get_user_model()


class RoleBasedNotificationPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == User.Role.MEMBER:
            return request.method in SAFE_METHODS

        if request.method == "POST" and getattr(view, "action", None) in [
            "create_notification_for_user",
            "create_notifications_by_habits",
        ]:
            return request.user.role == User.Role.ADMIN

        return request.user.role == User.Role.ADMIN


class IsNotificationOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.recipient
