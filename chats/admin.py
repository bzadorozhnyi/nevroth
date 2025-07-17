from django.contrib import admin

from chats.models import Chat, ChatMember, ChatMessage


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


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "content_short", "created_at", "updated_at")
    list_filter = ("chat", "sender", "created_at")
    search_fields = ("content", "sender__full_name", "chat__id")
    readonly_fields = ("created_at", "updated_at")

    def content_short(self, obj):
        return obj.content if len(obj.content) <= 50 else obj.content[:47] + "..."

    content_short.short_description = "Content"
