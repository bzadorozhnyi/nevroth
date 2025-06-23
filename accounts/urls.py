from django.urls.conf import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts.views import RegistrationView, RequestForgotPasswordView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token
    path('register/', RegistrationView.as_view(), name='register'),

    path(
        'auth/password/reset-request/',
        RequestForgotPasswordView.as_view(),
        name='request_forgot_password'
    ),
]
