from django.conf import settings
from django.db import models
from django.utils.text import slugify


class PlaceTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Place(models.Model):
    CATEGORY_CHOICES = [
        ('coffee', 'Кофе и завтраки'),
        ('food', 'Обеды и ужины'),
        ('bar', 'Бары и вечеринки'),
        ('walk', 'Прогулки и необычные места'),
        ('music', 'Живая музыка'),
        ('other', 'Другое'),
    ]

    SOURCE_CHOICES = [
        ('manual', 'Добавлено вручную'),
        ('import', 'Импорт'),
        ('yandex_api', 'Yandex API'),
    ]

    ATMOSPHERE_CHOICES = [
        ('party', 'Шумно и тусовочно'),
        ('cozy', 'Уютно и камерно'),
        ('romantic', 'Романтично'),
        ('tasty', 'Главное — вкусно'),
        ('work', 'Подходит для работы'),
        ('other', 'Другое'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    short_description = models.CharField(max_length=300)
    full_description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    metro = models.CharField(max_length=100, blank=True)
    average_check = models.PositiveIntegerField(null=True, blank=True)
    atmosphere = models.CharField(max_length=30, choices=ATMOSPHERE_CHOICES, default='other')
    tags_text = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(PlaceTag, blank=True, related_name='places')
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='manual')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_places'
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Place.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='places/', blank=True, null=True)
    external_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'Фото для {self.place.title}'
    