from django.conf import settings
from django.db import models


class BookingRequest(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_REJECTED = 'rejected'
    STATUS_ALTERNATIVE_OFFERED = 'alternative_offered'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_CONFIRMED, 'Подтверждена'),
        (STATUS_REJECTED, 'Отклонена'),
        (STATUS_ALTERNATIVE_OFFERED, 'Предложена альтернатива'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_requests'
    )
    place = models.ForeignKey(
        'places.Place',
        on_delete=models.CASCADE,
        related_name='booking_requests'
    )

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    guests_count = models.PositiveIntegerField(default=2)
    comment = models.TextField(blank=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    admin_comment = models.TextField(blank=True)
    alternative_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.id} — {self.user.email} — {self.place.title}'
    