from django.contrib import admin
from django.utils.html import format_html

from .models import BookingRequest


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'place',
        'booking_date',
        'booking_time',
        'guests_count',
        'status',
        'preference_summary',
        'created_at',
    )
    list_filter = ('status', 'booking_date', 'created_at')
    search_fields = ('user__email', 'name', 'phone', 'place__title')
    readonly_fields = (
        'user',
        'place',
        'name',
        'phone',
        'booking_date',
        'booking_time',
        'guests_count',
        'comment',
        'created_at',
        'updated_at',
        'user_preferences_block',
        'user_swipes_block',
    )

    fieldsets = (
        ('Данные заявки', {
            'fields': (
                'user', 'place', 'name', 'phone',
                'booking_date', 'booking_time', 'guests_count', 'comment'
            )
        }),
        ('Анкета пользователя', {
            'fields': ('user_preferences_block',)
        }),
        ('Реакции пользователя', {
            'fields': ('user_swipes_block',)
        }),
        ('Работа администратора', {
            'fields': ('status', 'admin_comment', 'alternative_text')
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def preference_summary(self, obj):
        prefs = getattr(obj.user, 'preferences', None)
        if not prefs:
            return 'Нет анкеты'
        return f'{prefs.get_purpose_display()} / {prefs.get_atmosphere_display()}'

    preference_summary.short_description = 'Анкета'

    def user_preferences_block(self, obj):
        prefs = getattr(obj.user, 'preferences', None)
        if not prefs:
            return 'Анкета не заполнена'
        return format_html(
            """
            <div>
                <p><strong>Бюджет:</strong> {}</p>
                <p><strong>Атмосфера:</strong> {}</p>
                <p><strong>Что ищет:</strong> {}</p>
                <p><strong>С кем гуляет:</strong> {}</p>
                <p><strong>Расстояние:</strong> {}</p>
                <p><strong>Дополнительно:</strong> {}</p>
            </div>
            """,
            prefs.get_budget_display(),
            prefs.get_atmosphere_display(),
            prefs.get_purpose_display(),
            prefs.get_company_type_display(),
            prefs.get_distance_display(),
            prefs.extra_text or '—',
        )

    user_preferences_block.short_description = 'Анкета пользователя'

    def user_swipes_block(self, obj):
        likes = obj.user.swipes.select_related('place').filter(action='like')[:20]
        dislikes = obj.user.swipes.select_related('place').filter(action='dislike')[:20]

        likes_html = '<br>'.join(f'• {item.place.title}' for item in likes) or '—'
        dislikes_html = '<br>'.join(f'• {item.place.title}' for item in dislikes) or '—'

        return format_html(
            """
            <div>
                <p><strong>Лайки:</strong><br>{}</p>
                <p><strong>Дизлайки:</strong><br>{}</p>
            </div>
            """,
            format_html(likes_html),
            format_html(dislikes_html),
        )

    user_swipes_block.short_description = 'Реакции пользователя'