from django.conf import settings
from django.db import models


class FavoriteFolder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_folders'
    )
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ('user', 'name')

    def __str__(self):
        return f'{self.name} ({self.user.email})'


class FavoriteItem(models.Model):
    folder = models.ForeignKey(
        FavoriteFolder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    place = models.ForeignKey(
        'places.Place',
        on_delete=models.CASCADE,
        related_name='favorite_items'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ('folder', 'place')

    def __str__(self):
        return f'{self.place.title} → {self.folder.name}'