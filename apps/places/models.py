from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Place(models.Model):
    CATEGORY_CHOICES = [
        ('coffee', 'Кофе и завтраки'),
        ('food', 'Обеды и ужины'),
        ('bar', 'Бары и вечеринки'),
        ('walk', 'Прогулки и необычные места'),
        ('other', 'Другое'),
    ]

    ATMOSPHERE_CHOICES = [
        ('party', 'Шумно и тусовочно'),
        ('cozy', 'Уютно и камерно'),
        ('romantic', 'Романтично'),
        ('tasty', 'Не важно, главное — чтобы вкусно'),
        ('other', 'Другое'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='Slug')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other', verbose_name='Категория')
    short_description = models.TextField(verbose_name='Краткое описание')
    full_description = models.TextField(blank=True, verbose_name='Полное описание')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    metro = models.CharField(max_length=120, blank=True, verbose_name='Метро')
    average_check = models.PositiveIntegerField(null=True, blank=True, verbose_name='Средний чек')
    atmosphere = models.CharField(max_length=30, choices=ATMOSPHERE_CHOICES, default='other', verbose_name='Атмосфера')
    tags_text = models.CharField(max_length=255, blank=True, verbose_name='Теги / ключевые слова')
    source = models.CharField(max_length=255, blank=True, default='', verbose_name='Источник')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_places',
        verbose_name='Кто добавил'
    )
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return self.title

    def _generate_unique_slug(self):
        base = slugify(self.title, allow_unicode=True).strip('-')
        if not base:
            base = 'place'

        slug = base
        counter = 1

        while Place.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f'{base}-{counter}'
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


class PlaceImage(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Место'
    )
    image = models.ImageField(upload_to='places/', blank=True, null=True, verbose_name='Файл')
    external_url = models.URLField(blank=True, verbose_name='Внешняя ссылка')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Изображение места'
        verbose_name_plural = 'Изображения мест'

    def __str__(self):
        return f'Изображение для {self.place.title}'

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return self.external_url