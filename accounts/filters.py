import django_filters
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserFilter(django_filters.FilterSet):
        query = django_filters.CharFilter(
        field_name="full_name",
        lookup_expr="icontains",
        help_text=_("Search by full name"),
        label=_("Search Query"),
    )
    habits = django_filters.BaseInFilter(
        field_name="habits__id",
        lookup_expr="in",
        help_text=_("Filter by habits (comma-separated IDs)"),
        label=_("Habits"),
    )

    class Meta:
        model = User
        fields = ["query", "habits"]

