from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers

from habits.models import UserHabit
from notifications.models import Notification, Message

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "recipient", "message", "is_read", "sent_at"]


class NotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id"]

    def update(self, instance, validated_data):
        instance.is_read = True
        instance.save(update_fields=["is_read"])

        return instance


class CreateNotificationForUserSerializer(serializers.Serializer):
    recipient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    text = serializers.CharField(required=True, max_length=300)

    @transaction.atomic
    def create(self, validated_data):
        recipient = validated_data.get("recipient")
        text = validated_data.get("text")
        sender = self.context["request"].user

        message = Message.objects.create(sender=sender, text=text)

        notification = Notification.objects.create(
            recipient=recipient,
            message=message,
        )

        return notification


class CreateNotificationsByHabitsResponseSerializer(serializers.Serializer):
    created = serializers.IntegerField()
    skipped = serializers.IntegerField()
    invalid_habits_ids = serializers.ListField(
        child=serializers.IntegerField(), default=[]
    )
    message = serializers.CharField()


class CreateNotificationsByHabitsSerializer(serializers.Serializer):
    habits_ids = serializers.ListSerializer(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
    text = serializers.CharField(required=True, max_length=300)

    @transaction.atomic
    def create(self, validated_data):
        habits_ids = validated_data.get("habits_ids")
        text = validated_data.get("text")
        sender = self.context["request"].user

        message = Message.objects.create(sender=sender, text=text)

        user_habits = UserHabit.objects.filter(habit__id__in=habits_ids).select_related(
            "user"
        )

        valid_habit_ids = set(user_habits.values_list("habit_id", flat=True))
        invalid_ids = list(set(habits_ids) - valid_habit_ids)

        notifications = [
            Notification(
                recipient=user_habit.user,
                message=message,
            )
            for user_habit in user_habits
        ]
        Notification.objects.bulk_create(notifications, batch_size=1000)

        created_count = len(notifications)

        response_data = {
            "created": created_count,
            "skipped": len(invalid_ids),
            "invalid_habits_ids": invalid_ids,
            "message": (
                f"Created {created_count} notification(s). "
                f"{len(invalid_ids)} habits IDs were invalid and ignored."
            ),
        }

        serialized_response = CreateNotificationsByHabitsResponseSerializer(
            data=response_data
        )
        serialized_response.is_valid(raise_exception=True)

        return serialized_response.data
