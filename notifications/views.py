from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import views
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
    PreSignedSerializer,
    ResponsePreSignedImageUploadSerializer,
)

from drf_spectacular.utils import extend_schema

from notifications.services.s3_service import S3Service


class NotificationViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()

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
        elif self.action == "create_notification_for_user":
            return CreateNotificationForUserSerializer
        elif self.action == "create_notifications_by_habits":
            return CreateNotificationsByHabitsSerializer

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

        serializer = self.get_serializer(notification, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={201: NotificationSerializer},
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="user",
        url_name="create_notification_for_user",
    )
    def create_notification_for_user(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        return Response(
            NotificationSerializer(notification).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        responses={201: CreateNotificationsByHabitsResponseSerializer},
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="habits",
        url_name="create_notifications_by_habits",
    )
    def create_notifications_by_habits(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=status.HTTP_201_CREATED)


class NotificationImageUploadView(views.APIView):
    action = "notification_image_upload"
    permission_classes = [RoleBasedNotificationPermission]

    @extend_schema(
        request=PreSignedSerializer,
        responses=ResponsePreSignedImageUploadSerializer,
        description="Generate presigned URL for uploading images for Notification",
    )
    def post(self, request, *args, **kwargs):
        serializer = PreSignedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            image_path, pre_signed_url = S3Service.generate_presign_url(
                image_extension=data["image_extension"],
                content_type=data.get("content_type", "application/octet-stream"),
            )

            return Response(
                {"image_path": image_path, "pre_signed_url": pre_signed_url},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
