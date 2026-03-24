from django.contrib import admin
from .models import FavoriteFolder, FavoriteItem


class FavoriteItemInline(admin.TabularInline):
    model = FavoriteItem
    extra = 0


@admin.register(FavoriteFolder)
class FavoriteFolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'created_at')
    search_fields = ('name', 'user__email')
    inlines = [FavoriteItemInline]


@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'folder', 'place', 'added_at')
    search_fields = ('folder__name', 'place__title', 'folder__user__email')
