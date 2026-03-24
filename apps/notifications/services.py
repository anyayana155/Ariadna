import json

from django.conf import settings
from django.core.mail import send_mail
from pywebpush import webpush, WebPushException

from .models import PushSubscription


def send_new_chat_email_notification(user, thread, text):
    prefs = getattr(user, 'notification_preferences', None)
    if prefs and not prefs.email_new_message:
        return

    if not user.email:
        return

    send_mail(
        subject='Новое сообщение в чате — Ариадна',
        message=(
            f'У вас новое сообщение в чате #{thread.id}.\n\n'
            f'Текст:\n{text}\n\n'
            f'Откройте сайт, чтобы ответить.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_new_chat_push_notification(user, thread, text):
    prefs = getattr(user, 'notification_preferences', None)
    if prefs and not prefs.push_new_message:
        return

    subscriptions = user.push_subscriptions.filter(is_active=True)

    payload = json.dumps({
        'title': 'Новое сообщение',
        'body': text[:120],
        'url': f'/chat/{thread.id}/',
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
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    'sub': f'mailto:{settings.DEFAULT_FROM_EMAIL}'
                }
            )
        except WebPushException:
            subscription.is_active = False
            subscription.save(update_fields=['is_active'])