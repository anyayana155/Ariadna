from django.urls import path

from .views import notification_settings_view


urlpatterns = [
    path('', notification_settings_view, name='notification_settings'),
]
