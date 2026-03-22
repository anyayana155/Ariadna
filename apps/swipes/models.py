from django.conf import settings
from django.db import models


class SwipeAction(models.Model):
    ACTION_CHOICES = [
        ('like', 'Лайк'),
        ('dislike', 'Дизлайк'),
        ('skip', 'Пропуск'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swipes')
    place = models.ForeignKey('places.Place', on_delete=models.CASCADE, related_name='swipes')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'place')

    def __str__(self):
        return f'{self.user} — {self.place} — {self.action}'