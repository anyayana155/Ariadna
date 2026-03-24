from django.conf import settings
from django.db import models


class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions'
    )
    endpoint = models.TextField(unique=True)
    p256dh_key = models.TextField()
    auth_key = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Push subscription for {self.user.email}'


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    email_chat = models.BooleanField(default=True)
    push_chat = models.BooleanField(default=True)

    email_booking = models.BooleanField(default=True)
    push_booking = models.BooleanField(default=True)

    email_system = models.BooleanField(default=True)
    push_system = models.BooleanField(default=True)

    def __str__(self):
        return f'Notification preferences for {self.user.email}'
