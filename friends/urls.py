from django.urls import path

from friends.views import SendFriendshipRequestView, CancelFriendshipRequestView

urlpatterns = [
    path(
        "friends/send-request/",
        SendFriendshipRequestView.as_view(),
        name="send-friendship-request",
    ),
    path(
        "friends/cancel-request/<int:pk>/",
        CancelFriendshipRequestView.as_view(),
        name="cancel-friendship-request",
    ),
]
