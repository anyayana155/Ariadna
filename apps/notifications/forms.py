from django import forms
from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_chat',
            'push_chat',
            'email_booking',
            'push_booking',
            'email_system',
            'push_system',
        ]
        labels = {
            'email_chat': 'Email — новые сообщения',
            'push_chat': 'Push — новые сообщения',
            'email_booking': 'Email — обновления заявок',
            'push_booking': 'Push — обновления заявок',
            'email_system': 'Email — системные уведомления',
            'push_system': 'Push — системные уведомления',
        }
