from django.contrib import admin

from chats.models import Chat, ChatMember


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_type", "created_at", "updated_at")
    list_filter = ("chat_type",)
    search_fields = ("id",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(ChatMember)
class ChatMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "user", "created_at")
    search_fields = ("user__full_name", "chat__id")
    list_filter = ("created_at",)
    autocomplete_fields = ("user", "chat")
    ordering = ("-created_at",)
