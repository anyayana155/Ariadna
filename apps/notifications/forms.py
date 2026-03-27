from django import forms
from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_chat',
            'email_booking',
            'email_system',
        ]
        labels = {
            'email_chat': 'Email — новые сообщения',
            'email_booking': 'Email — обновления заявок',
            'email_system': 'Email — системные уведомления',
        }
