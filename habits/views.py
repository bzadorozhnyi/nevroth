from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from habits.models import Habit, UserHabit
from habits.permissions import RoleBasedHabitPermission
from habits.serializers import HabitSerializer, UserHabitsUpdateSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [RoleBasedHabitPermission]

    @action(
        detail=False,
        methods=["POST"],
        url_path="select",
        url_name="select-habits"
    )
    def select_user_habits(self, request):
        serializer = UserHabitsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        habit_ids = serializer.validated_data["habits_ids"]

        # Remove previous habits
        UserHabit.objects.filter(user=user).delete()

        new_user_habits = [UserHabit(user=user, habit_id=habit_id) for habit_id in habit_ids]
        UserHabit.objects.bulk_create(new_user_habits)

        return Response({"detail": _("Habits updated successfully")}, status=status.HTTP_200_OK)
