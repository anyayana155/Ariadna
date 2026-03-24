from django.contrib import admin
from .models import PushSubscription, NotificationPreference


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__email', 'endpoint')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'email_chat',
        'email_booking',
        'push_chat',
        'push_booking',
    )
    search_fields = ('user__email',)
