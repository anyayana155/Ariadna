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
        'email_new_message',
        'email_booking_updates',
        'push_new_message',
        'push_booking_updates',
    )
    search_fields = ('user__email',)
