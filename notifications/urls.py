from django.urls.conf import path, include

from rest_framework.routers import DefaultRouter

from notifications.views import NotificationViewSet, NotificationImageUploadView

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "notification-presigned-url/",
        NotificationImageUploadView.as_view(),
        name="notification-presigned-url",
    ),
]
