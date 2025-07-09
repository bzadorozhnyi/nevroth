from django.urls import path

from friends.views import SendFriendshipRequestView

urlpatterns = [
    path(
        "friends/send-request/",
        SendFriendshipRequestView.as_view(),
        name="send-friendship-request",
    ),
]
