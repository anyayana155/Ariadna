from django.contrib import admin
from .models import Place, PlaceImage, PlaceTag


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'metro',
        'average_check',
        'atmosphere',
        'is_published',
        'created_at',
    )
    list_filter = ('category', 'atmosphere', 'is_published', 'source')
    search_fields = ('title', 'address', 'metro', 'tags_text')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PlaceImageInline]


@admin.register(PlaceTag)
class PlaceTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
