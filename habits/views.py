from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, OpenApiResponse

from habits.filters import HabitFilter, HabitProgressFilter
from habits.models import Habit, HabitProgress, UserHabit
from habits.permissions import RoleBasedHabitPermission
from habits.serializers import HabitSerializer, UserHabitsUpdateSerializer, HabitProgressSerializer, \
    HabitStreaksSerializer
from habits.services.calculate_streak import CalculateStreakService


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [RoleBasedHabitPermission]
    filterset_class = HabitFilter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name", "description"]

    @extend_schema(
        request=UserHabitsUpdateSerializer,
        responses={200: OpenApiResponse(description="Habits updated successfully")},
    )
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
        if getattr(self, "swagger_fake_view", False):
            return HabitProgress.objects.none()

        return HabitProgress.objects.filter(user=self.request.user)


class HabitStreaksView(APIView):
    @extend_schema(
        responses={
            200: HabitStreaksSerializer,
            404: OpenApiResponse(description="Habit not found or not associated with user")
        },
    )
    def get(self, request, habit_id):
        if not UserHabit.objects.filter(habit=habit_id, user=request.user.id).first():
            return Response({"detail": _("Habit not found or not associated with user")},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = HabitStreaksSerializer(instance={}, context={"user_id": request.user.id, "habit_id": habit_id})
        return Response(serializer.data, status=status.HTTP_200_OK)
