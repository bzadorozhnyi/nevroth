from datetime import datetime

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from rest_framework import serializers

from habits import models
from habits.constants import REQUIRED_HABITS_COUNT, HABIT_FAIL_UPDATE_TIMEOUT_SECONDS
from habits.models import Habit, UserHabit, HabitProgress
from habits.services.calculate_streak import CalculateStreakService


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id", "name", "description"]


class UserHabitsUpdateSerializer(serializers.Serializer):
    habits_ids = serializers.ListSerializer(
        child=serializers.IntegerField(),
        allow_empty=False,
    )

    def save(self, **kwargs):
        user = self.context["request"].user
        habit_ids = self.validated_data["habits_ids"]

        # Remove previous habits
        UserHabit.objects.filter(user=user).delete()

        # Add new ones
        new_user_habits = [
            UserHabit(user=user, habit_id=habit_id) for habit_id in habit_ids
        ]
        UserHabit.objects.bulk_create(new_user_habits)

        return {"detail": _("Habits updated successfully")}

    def validate_habits_ids(self, value):
        if len(value) != REQUIRED_HABITS_COUNT:
            raise serializers.ValidationError(
                f"Exactly {REQUIRED_HABITS_COUNT} habits must be provided"
            )

        if len(set(value)) != REQUIRED_HABITS_COUNT:
            raise serializers.ValidationError("Habits must be unique")

        existing_habits = models.Habit.objects.filter(id__in=value).values_list(
            "id", flat=True
        )
        missing_ids = [
            habit_id for habit_id in value if habit_id not in existing_habits
        ]

        if missing_ids:
            raise serializers.ValidationError(
                f"These habit IDs do not exist: {missing_ids}"
            )

        return value


class HabitProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitProgress
        fields = ["habit", "date", "status"]
        read_only_fields = ["date"]

    def create(self, validated_data):
        user = self.context["request"].user
        habit = validated_data.get("habit")
        date = datetime.now().date()

        habit_progress, created = HabitProgress.objects.get_or_create(
            user=user,
            habit=habit,
            date=date,
            defaults={"status": validated_data.get("status")},
        )

        if not created:
            time_diff = timezone.now() - habit_progress.updated_at
            if (
                habit_progress.status == HabitProgress.Status.FAIL
                and time_diff.total_seconds() > HABIT_FAIL_UPDATE_TIMEOUT_SECONDS
            ):
                raise serializers.ValidationError(
                    _(
                        f"Cannot update failed progress after {HABIT_FAIL_UPDATE_TIMEOUT_SECONDS} seconds"
                    )
                )

            habit_progress.status = validated_data.get("status")
            habit_progress.save()

        return habit_progress


class HabitStreaksSerializer(serializers.Serializer):
    current = serializers.IntegerField(read_only=True)
    max = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        user_id = self.context["user_id"]
        habit_id = self.context["habit_id"]

        return CalculateStreakService.calculate_streaks(
            user_id=user_id, habit_id=habit_id
        )
