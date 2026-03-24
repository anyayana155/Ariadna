from django.db.models.signals import pre_save, post_save
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
def notify_booking_status_changed(sender, instance, created, **kwargs):
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    if old_status == new_status:
        return

    user = instance.user
    place = instance.place

    status_label = instance.get_status_display()

    message_lines = [
        f'Статус вашей заявки #{instance.id} изменён.',
        f'Место: {place.title}',
        f'Новый статус: {status_label}',
    ]

    if instance.admin_comment:
        message_lines.append(f'Комментарий администратора: {instance.admin_comment}')

    if instance.alternative_text:
        message_lines.append(f'Предложенная альтернатива: {instance.alternative_text}')

    message = '\n\n'.join(message_lines)

    send_email_notification(
        user,
        subject='Обновление заявки — Ариадна',
        message=message,
        category='booking'
    )

    send_push_notification(
        user,
        title='Обновление заявки',
        body=f'{place.title}: {status_label}',
        url=f'/bookings/{instance.id}/',
        category='booking'
    )
