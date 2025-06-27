from rest_framework import serializers

from habits import models
from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'description']


class UserHabitsUpdateSerializer(serializers.Serializer):
    habits_ids = serializers.ListSerializer(
        child=serializers.IntegerField(),
        allow_empty=False,
    )

    def validate_habits_ids(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Exactly 3 habits must be provided")

        if list(set(value)) != value:
            raise serializers.ValidationError("Habits must be unique")

        existing_habits = models.Habit.objects.filter(id__in=value).values_list("id", flat=True)
        missing_ids = [habit_id for habit_id in value if habit_id not in existing_habits]

        if missing_ids:
            raise serializers.ValidationError(f"These habit IDs do not exist: {missing_ids}")

        return value
