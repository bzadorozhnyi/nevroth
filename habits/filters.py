import django_filters
from django.utils.translation import gettext_lazy as _

from habits.models import Habit, HabitProgress


class HabitFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Habit
        fields = ["name"]


class HabitProgressFilter(django_filters.FilterSet):
    habit = django_filters.NumberFilter(
        field_name="habit__id",
        help_text=_("Filter habits progress by habit id"),
    )
    date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="exact",
        help_text=_("Filter habits progress by this date (YYYY-MM-DD)"),
    )
    from_date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        help_text=_("Filter habits progress from this date (YYYY-MM-DD)"),
    )
    to_date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        help_text=_("Filter habits progress until this date (YYYY-MM-DD)"),
    )

    class Meta:
        model = HabitProgress
        fields = ["habit", "date", "from_date", "to_date"]
