from django.conf import settings
from django.db import models


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    email_chat = models.BooleanField(default=True)
    email_booking = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)

    def __str__(self):
        return f'Notification preferences for {self.user.email}'
