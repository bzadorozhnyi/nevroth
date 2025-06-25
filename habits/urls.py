from django.urls.conf import path, include

from rest_framework.routers import DefaultRouter

from habits.views import HabitViewSet

router = DefaultRouter()
router.register('habits', HabitViewSet, basename='habits')

urlpatterns = [
    path('', include(router.urls)),
]
