from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from accounts.filters import UserFilter
from accounts.serializers import (
    RegistrationSerializer,
    RequestForgotTokenSerializer,
    UpdateForgottenPasswordSerializer,
    CurrentUserSerializer,
    UserSearchResultSerializer,
    UserSuggestionSerializer,
)
from accounts.services.user import UserService

User = get_user_model()


class CurrentUserProfileView(RetrieveUpdateAPIView):
    serializer_class = CurrentUserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user


class RegistrationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class RequestForgotPasswordView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RequestForgotTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            if User.objects.filter(email=email).exists():
                serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateForgottenPasswordView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UpdateForgottenPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UsersSearchView(ListAPIView):
    serializer_class = UserSearchResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()

        return User.objects.with_relation_status(self.request.user)


class SuggestedFriendsListView(ListAPIView):
    serializer_class = UserSuggestionSerializer

    def get_queryset(self):
        return UserService.get_suggested_users(self.request.user)
