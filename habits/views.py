from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework import filters
from rest_framework import generics

from django_filters.rest_framework import DjangoFilterBackend

from habits.filters import HabitFilter, HabitProgressFilter
from habits.models import Habit, HabitProgress
from habits.permissions import RoleBasedHabitPermission
from habits.serializers import HabitSerializer, UserHabitsUpdateSerializer, HabitProgressSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [RoleBasedHabitPermission]
    filterset_class = HabitFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name", "description"]

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


class HabitProgressViewSet(generics.ListCreateAPIView):
    serializer_class = HabitProgressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = HabitProgressFilter

    def get_queryset(self):
        return HabitProgress.objects.filter(user=self.request.user)
