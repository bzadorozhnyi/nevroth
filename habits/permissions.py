from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

User = get_user_model()


class RoleBasedHabitPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if (
                request.method == "POST" and
                getattr(view, "action", None) == "select_user_habits"
        ):
            return request.user.role == User.Role.MEMBER

        if request.user.role == User.Role.MEMBER:
            return request.method in SAFE_METHODS

        return request.user.role == User.Role.ADMIN
