import json

from django.conf import settings
from django.core.mail import send_mail
from pywebpush import WebPushException, webpush


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


def send_push_notification(user, title, body, url, category):
    prefs = getattr(user, 'notification_preferences', None)
    if not prefs:
        return

    if category == 'chat' and not prefs.push_chat:
        return
    if category == 'booking' and not prefs.push_booking:
        return
    if category == 'system' and not prefs.push_system:
        return

    if not getattr(settings, 'VAPID_PRIVATE_KEY', None):
        print('PUSH ERROR: no VAPID_PRIVATE_KEY')
        return

    subscriptions = user.push_subscriptions.filter(is_active=True)

    payload = json.dumps({
        'title': title,
        'body': body,
        'url': url,
    })

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {
                        'p256dh': subscription.p256dh_key,
                        'auth': subscription.auth_key,
                    },
                },
                data=payload,
                vapid_private_key=str(settings.VAPID_PRIVATE_KEY),
                vapid_claims={
                    'sub': f'mailto:{settings.DEFAULT_FROM_EMAIL}'
                }
            )
            print('PUSH SENT')

        except WebPushException as e:
            print('PUSH ERROR:', e)
            subscription.is_active = False
            subscription.save(update_fields=['is_active'])
