from django.urls.conf import path, include

from rest_framework.routers import DefaultRouter

from habits.views import HabitViewSet, HabitProgressViewSet, HabitStreaksView

router = DefaultRouter()
router.register('habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    path('habits-progress/', HabitProgressViewSet.as_view(), name='habit-progress'),
    path('habits-progress/streaks/<int:habit_id>/', HabitStreaksView.as_view(), name='habit-progress-streak'),
]
