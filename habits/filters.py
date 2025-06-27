import django_filters

from habits.models import Habit


class HabitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Habit
        fields = ["name"]
