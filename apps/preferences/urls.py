from django.urls import path
from .views import preference_create_or_update_view, preference_edit_view

urlpatterns = [
    path('', preference_create_or_update_view, name='preferences'),
    path('edit/', preference_edit_view, name='preferences_edit'),
]