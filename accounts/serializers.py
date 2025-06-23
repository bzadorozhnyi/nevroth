from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import VerifyToken

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "full_name", "password"]

    def create(self, validated_data):
        validated_data["role"] = User.Role.INSTALLER
        return User.objects.create_user(**validated_data)


class RequestForgotTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        if user := User.objects.filter(email=validated_data["email"]).first():
            token = VerifyToken.objects.create(user=user, email=validated_data["email"])
            token.send_email_to_restore_password()

            return token
