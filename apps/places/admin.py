from django.contrib import admin

from .models import Place, PlaceImage


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 0
    fields = ('image', 'external_url', 'order')


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'metro',
        'average_check',
        'is_published',
        'created_at',
    )
    list_filter = ('category', 'atmosphere', 'is_published', 'created_at')
    search_fields = ('title', 'address', 'metro', 'tags_text')
    prepopulated_fields = {}
    inlines = [PlaceImageInline]


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ('place', 'order')
    search_fields = ('place__title', 'external_url')
