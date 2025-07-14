from django.urls import path

from friends.views import (
    SendFriendshipRequestView,
    CancelFriendshipRequestView,
    AcceptFriendshipRequestView,
    RejectFriendshipRequestView,
    RemoveFriendView,
    FriendsListView,
)

urlpatterns = [
    path(
        "friends-request/",
        SendFriendshipRequestView.as_view(),
        name="send-friendship-request",
    ),
    path(
        "friends-request/<int:user_id>/cancel/",
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
    path("friends/", FriendsListView.as_view(), name="friends-list"),
    path(
        "friends/<int:user_id>/",
        RemoveFriendView.as_view(),
        name="remove-friend",
    ),
]
