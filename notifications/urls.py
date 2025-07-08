from django.urls.conf import path, include

from rest_framework.routers import DefaultRouter

from notifications.views import NotificationViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
]
