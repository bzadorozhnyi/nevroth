from django.urls.conf import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts.views import (
    RegistrationView,
    RequestForgotPasswordView,
    UpdateForgottenPasswordView,
    CurrentUserProfileView,
    UsersSearchView,
    SuggestedFriendsListView,
)

urlpatterns = [
    path("user-profile/", CurrentUserProfileView.as_view(), name="user-profile"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # Login
    path(
        "token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),  # Refresh token
    path("register/", RegistrationView.as_view(), name="register"),
    path(
        "auth/password/reset-request/",
        RequestForgotPasswordView.as_view(),
        name="request_forgot_password",
    ),
    path(
        "auth/password/reset/",
        UpdateForgottenPasswordView.as_view(),
        name="update_forgot_password",
    ),
    path("users/", UsersSearchView.as_view(), name="users"),
    path(
        "users/suggestions/",
        SuggestedFriendsListView.as_view(),
        name="suggested-friends-list",
    ),
]
