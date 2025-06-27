from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from accounts.models import VerifyToken
from habits.models import UserHabit

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=User.Role.choices)
    selected_habits = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = (
            "password",
            "habits",
            "created_at",
            "updated_at",
            "is_staff",
            "is_superuser",
            "last_login",
        )

    def validate_role(self, value):
        if self.instance and value != self.instance.role:
            raise serializers.ValidationError("You are not allowed to change your role")
        return value

    def get_selected_habits(self, obj):
        return UserHabit.objects.filter(user=obj).exists()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "full_name", "password"]

    def create(self, validated_data):
        validated_data["role"] = User.Role.MEMBER
        return User.objects.create_user(**validated_data)


class RequestForgotTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        if user := User.objects.filter(email=validated_data["email"]).first():
            token = VerifyToken.objects.create(user=user, email=validated_data["email"])
            token.send_email_to_restore_password()

            return token


class UpdateForgottenPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField()

    def validate_password(self, value):
        user = self.context["request"].user
        validate_password(value, user=user)
        return value

    def validate(self, data):
        verify_token = VerifyToken.objects.filter(token=data["token"]).first()
        if not verify_token:
            raise serializers.ValidationError(_("The link is not found"))

        data["verify_token"] = verify_token

        return data

    def create(self, validated_data):
        verify_token = validated_data.get("verify_token")

        user = User.objects.filter(email=verify_token.email).first()
        user.set_password(validated_data["password"])
        user.save()

        verify_token.delete()

        return user
