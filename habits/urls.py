from django.urls.conf import path, include

from rest_framework.routers import DefaultRouter

from habits.views import HabitViewSet, HabitProgressViewSet

router = DefaultRouter()
router.register('habits', HabitViewSet, basename='habit')
router.register('habits-progress', HabitProgressViewSet, basename='habit-progress')

urlpatterns = [
    path('', include(router.urls)),
]
