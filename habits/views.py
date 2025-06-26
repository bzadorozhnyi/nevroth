from rest_framework import viewsets

from habits.models import Habit
from habits.permissions import RoleBasedHabitPermission
from habits.serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [RoleBasedHabitPermission]
