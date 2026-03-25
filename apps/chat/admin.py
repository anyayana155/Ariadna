from django.contrib import admin
from django.utils.html import format_html

from .models import ChatThread, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'text', 'created_at')
    can_delete = False


@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'assigned_admin', 'is_closed', 'updated_at')
    list_filter = ('is_closed', 'created_at', 'updated_at')
    search_fields = ('user__email', 'assigned_admin__email')
    readonly_fields = (
        'user_info_block',
        'user_preferences_block',
        'user_likes_block',
        'user_dislikes_block',
        'user_folders_block',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        ('Чат', {
            'fields': ('user', 'assigned_admin', 'is_closed')
        }),
        ('Быстрый доступ к пользователю', {
            'fields': ('user_info_block', 'user_preferences_block')
        }),
        ('Реакции пользователя', {
            'fields': ('user_likes_block', 'user_dislikes_block')
        }),
        ('Папки пользователя', {
            'fields': ('user_folders_block',)
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [ChatMessageInline]

    def user_info_block(self, obj):
        profile = getattr(obj.user, 'profile', None)
        display_name = profile.display_name if profile else ''
        return format_html(
            """
            <div>
                <p><strong>Email:</strong> {}</p>
                <p><strong>Имя:</strong> {}</p>
            </div>
            """,
            obj.user.email,
            display_name or obj.user.first_name or '—',
        )

    user_info_block.short_description = 'Пользователь'

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

    user_preferences_block.short_description = 'Анкета'

    def user_likes_block(self, obj):
        likes = obj.user.swipes.select_related('place').filter(action='like')[:30]
        html = '<br>'.join(f'• {item.place.title}' for item in likes) or '—'
        return format_html(html)

    user_likes_block.short_description = 'Лайки'

    def user_dislikes_block(self, obj):
        dislikes = obj.user.swipes.select_related('place').filter(action='dislike')[:30]
        html = '<br>'.join(f'• {item.place.title}' for item in dislikes) or '—'
        return format_html(html)

    user_dislikes_block.short_description = 'Дизлайки'

    def user_folders_block(self, obj):
        folders = obj.user.favorite_folders.prefetch_related('items__place').all()
        if not folders:
            return 'Папок нет'

        parts = []
        for folder in folders:
            places = ', '.join(item.place.title for item in folder.items.all()[:20]) or 'Пусто'
            parts.append(f'<p><strong>{folder.name}</strong>: {places}</p>')

        return format_html(''.join(parts))

    user_folders_block.short_description = 'Папки'
