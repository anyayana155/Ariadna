from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.notifications.services import send_email_notification, send_push_notification
from .models import BookingRequest


@receiver(pre_save, sender=BookingRequest)
def store_old_booking_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old_instance = BookingRequest.objects.get(pk=instance.pk)
        instance._old_status = old_instance.status
    except BookingRequest.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=BookingRequest)
def notify_booking_events(sender, instance, created, **kwargs):
    if created:
        admins = type(instance.user).objects.filter(is_staff=True, is_active=True)
        message = (
            f'Новая заявка #{instance.id}\n\n'
            f'Пользователь: {instance.user.email}\n'
            f'Место: {instance.place.title}\n'
            f'Дата: {instance.booking_date}\n'
            f'Время: {instance.booking_time}\n'
            f'Гостей: {instance.guests_count}'
        )

        for admin in admins:
            send_email_notification(
                admin,
                subject='Новая заявка — Ариадна',
                message=message,
                category='booking',
            )
            send_push_notification(
                admin,
                title='Новая заявка',
                body=f'{instance.place.title} — {instance.user.email}',
                url=f'/dashboard/bookings/{instance.id}/',
                category='booking',
            )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status == instance.status:
        return

    status_label = instance.get_status_display()
    lines = [
        f'Статус вашей заявки #{instance.id} изменён.',
        f'Место: {instance.place.title}',
        f'Новый статус: {status_label}',
    ]

    if instance.admin_comment:
        lines.append(f'Комментарий администратора: {instance.admin_comment}')

    if instance.alternative_text:
        lines.append(f'Предложенная альтернатива: {instance.alternative_text}')

    message = '\n\n'.join(lines)

    send_email_notification(
        instance.user,
        subject='Обновление заявки — Ариадна',
        message=message,
        category='booking',
    )
    send_push_notification(
        instance.user,
        title='Обновление заявки',
        body=f'{instance.place.title}: {status_label}',
        url=f'/bookings/{instance.id}/',
        category='booking',
    )
