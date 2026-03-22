from django.contrib import admin
from .models import SwipeAction


@admin.register(SwipeAction)
class SwipeActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'place__title')
