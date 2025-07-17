from django.urls.conf import path, include

from rest_framework.routers import DefaultRouter

from chats.views import ChatListCreateView, ChatMessageView, ChatMessageListView

router = DefaultRouter()
router.register("messages", ChatMessageView, basename="chat-message")

urlpatterns = [
    path(
        "chats/",
        ChatListCreateView.as_view(),
        name="chat-list-create",
    ),
    path(
        "chats/<int:id>/messages/",
        ChatMessageListView.as_view(),
        name="chat-messages-list",
    ),
    path("", include(router.urls)),
]
