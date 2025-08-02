from django.contrib import admin
from .models import NotificationMessage, Notification


@admin.register(NotificationMessage)
class NotificationMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "short_text", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "sender__email", "sender__username")
    ordering = ("-created_at",)

    def short_text(self, obj):
        return (obj.text[:50] + "...") if len(obj.text) > 50 else obj.text

    short_text.short_description = "Text"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "is_read", "sent_at", "message_preview")
    list_filter = ("is_read", "sent_at")
    search_fields = ("recipient__username", "recipient__email", "message__text")
    ordering = ("-sent_at",)

    def message_preview(self, obj):
        return (
            (obj.message.text[:50] + "...")
            if len(obj.message.text) > 50
            else obj.message.text
        )

    message_preview.short_description = "Message"
