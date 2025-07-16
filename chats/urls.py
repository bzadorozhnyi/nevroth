from django.urls.conf import path

from chats.views import ChatListCreateView

urlpatterns = [
    path(
        "chats/",
        ChatListCreateView.as_view(),
        name="chat-list-create",
    ),
]
