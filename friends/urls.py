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
        "friends-request/",
        SendFriendshipRequestView.as_view(),
        name="send-friendship-request",
    ),
    path(
        "friends-request/<int:user_id>/",
        CancelFriendshipRequestView.as_view(),
        name="cancel-friendship-request",
    ),
    path(
        "friends-request/<int:user_id>/accept/",
        AcceptFriendshipRequestView.as_view(),
        name="accept-friendship-request",
    ),
    path(
        "friends-request/<int:user_id>/reject/",
        RejectFriendshipRequestView.as_view(),
        name="reject-friendship-request",
    ),
    path(
        "friends/remove-friend/",
        RemoveFriendView.as_view(),
        name="remove-friend",
    ),
]
