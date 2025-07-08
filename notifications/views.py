from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status

from notifications.models import Notification
from notifications.permissions import (
    RoleBasedNotificationPermission,
    IsNotificationOwner,
)
from notifications.serializers import (
    CreateNotificationForUserSerializer,
    NotificationSerializer,
    CreateNotificationsByHabitsSerializer,
    NotificationReadSerializer,
    CreateNotificationsByHabitsResponseSerializer,
)

from drf_spectacular.utils import extend_schema


class NotificationViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by(
            "-sent_at"
        )

    def get_permissions(self):
        if hasattr(self, "action"):
            if self.action in ["destroy", "mark_as_read"]:
                return [IsNotificationOwner()]
        return [RoleBasedNotificationPermission()]

    def get_serializer_class(self):
        if self.action == "mark_as_read":
            return NotificationReadSerializer

        return NotificationSerializer

    @extend_schema(responses={204: None})
    @action(
        detail=True,
        methods=["PATCH"],
        url_path="mark-as-read",
        url_name="mark_as_read",
    )
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()

        serializer = NotificationReadSerializer(notification, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=CreateNotificationForUserSerializer,
        responses={201: NotificationSerializer},
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="user",
        url_name="create_notification_for_user",
    )
    def create_notification_for_user(self, request):
        serializer = CreateNotificationForUserSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        return Response(
            NotificationSerializer(notification).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        request=CreateNotificationsByHabitsSerializer,
        responses={201: CreateNotificationsByHabitsResponseSerializer},
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="habits",
        url_name="create_notifications_by_habits",
    )
    def create_notifications_by_habits(self, request):
        serializer = CreateNotificationsByHabitsSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=status.HTTP_201_CREATED)
