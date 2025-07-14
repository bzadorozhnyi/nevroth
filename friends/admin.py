from django.contrib import admin
from friends.models import FriendsRelation


@admin.register(FriendsRelation)
class FriendsRelationAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("from_user__username", "to_user__username")
    autocomplete_fields = ("from_user", "to_user")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("from_user", "to_user")
