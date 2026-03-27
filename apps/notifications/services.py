from django.conf import settings
from django.core.mail import send_mail


def send_email_notification(user, subject, message, category):
    prefs = getattr(user, 'notification_preferences', None)
    if not prefs:
        return

    if category == 'chat' and not prefs.email_chat:
        return
    if category == 'booking' and not prefs.email_booking:
        return
    if category == 'system' and not prefs.email_system:
        return

    if not user.email:
        return

    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print('EMAIL SENT RESULT:', result)
    except Exception as e:
        print('EMAIL ERROR:', e)
