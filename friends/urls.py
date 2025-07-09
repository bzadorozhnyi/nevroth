from django.urls import path

from friends.views import (
    SendFriendshipRequestView,
    CancelFriendshipRequestView,
    AcceptFriendshipRequestView,
    RejectFriendshipRequestView,
    RemoveFriendView,
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
        "friends/accept-request/<int:pk>/",
        AcceptFriendshipRequestView.as_view(),
        name="accept-friendship-request",
    ),
    path(
        "friends/reject-request/<int:pk>/",
        RejectFriendshipRequestView.as_view(),
        name="reject-friendship-request",
    ),
    path(
        "friends/remove-friend/",
        RemoveFriendView.as_view(),
        name="remove-friend",
    ),
]
