from django.conf import settings
from django.db import models


class PreferenceProfile(models.Model):
    BUDGET_CHOICES = [
        ('low', 'Бюджетно (до 500 ₽)'),
        ('medium', 'Средний (500–1500 ₽)'),
        ('high', 'Выше среднего (1500–3000 ₽)'),
        ('any', 'Не важно, главное — атмосфера'),
    ]

    ATMOSPHERE_CHOICES = [
        ('party', 'Шумно и тусовочно'),
        ('cozy', 'Уютно и камерно'),
        ('romantic', 'Романтично'),
        ('tasty', 'Не важно, главное — чтобы вкусно'),
    ]

    PURPOSE_CHOICES = [
        ('coffee', 'Кофе и завтраки'),
        ('lunch', 'Обеды и ужины'),
        ('bars', 'Бары и вечеринки'),
        ('walks', 'Прогулки и необычные места'),
        ('all', 'Всё сразу'),
    ]

    COMPANY_CHOICES = [
        ('friends', 'С друзьями'),
        ('partner', 'С партнёром'),
        ('alone', 'Один/одна'),
        ('group', 'С компанией (4+ человек)'),
    ]

    DISTANCE_CHOICES = [
        ('5_10', '5–10 минут пешком'),
        ('15_20', '15–20 минут пешком'),
        ('transport', 'Готов/а доехать пару остановок'),
        ('any', 'Не важно'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    atmosphere = models.CharField(max_length=20, choices=ATMOSPHERE_CHOICES)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    company_type = models.CharField(max_length=20, choices=COMPANY_CHOICES)
    distance = models.CharField(max_length=20, choices=DISTANCE_CHOICES)
    extra_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Анкета {self.user.email}'