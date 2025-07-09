from django.urls import path

from friends.views import (
    SendFriendshipRequestView,
    CancelFriendshipRequestView,
    AcceptFriendshipRequestView,
    RejectFriendshipRequestView,
)

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
    path(
        "friends/accept/<int:pk>/",
        AcceptFriendshipRequestView.as_view(),
        name="accept-friendship-request",
    ),
    path(
        "friends/reject/<int:pk>/",
        RejectFriendshipRequestView.as_view(),
        name="reject-friendship-request",
    ),
]
