from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from habits import models
from habits.constants import REQUIRED_HABITS_COUNT
from habits.models import Habit, UserHabit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'description']


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
        new_user_habits = [UserHabit(user=user, habit_id=habit_id) for habit_id in habit_ids]
        UserHabit.objects.bulk_create(new_user_habits)

        return {"detail": _("Habits updated successfully")}

    def validate_habits_ids(self, value):
        if len(value) != REQUIRED_HABITS_COUNT:
            raise serializers.ValidationError(f"Exactly {REQUIRED_HABITS_COUNT} habits must be provided")

        if len(set(value)) != REQUIRED_HABITS_COUNT:
            raise serializers.ValidationError("Habits must be unique")

        existing_habits = models.Habit.objects.filter(id__in=value).values_list("id", flat=True)
        missing_ids = [habit_id for habit_id in value if habit_id not in existing_habits]

        if missing_ids:
            raise serializers.ValidationError(f"These habit IDs do not exist: {missing_ids}")

        return value
