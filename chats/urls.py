from django.urls.conf import path

from chats.views import ChatListView

urlpatterns = [
    path(
        "chats/",
        ChatListView.as_view(),
        name="chat-list",
    )
]
