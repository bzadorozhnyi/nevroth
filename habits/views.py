from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from habits.models import Habit
from habits.permissions import RoleBasedHabitPermission
from habits.serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [RoleBasedHabitPermission]
