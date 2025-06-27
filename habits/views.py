from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from habits.models import Habit
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
        serializer = UserHabitsUpdateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=status.HTTP_200_OK)
