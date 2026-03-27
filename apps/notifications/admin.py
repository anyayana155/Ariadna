from django.contrib import admin
from .models import NotificationPreference


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'email_chat',
        'email_booking',
        'email_system',
    )
