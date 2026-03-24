from django.urls import path

from .views import notification_settings_view, save_push_subscription_view


urlpatterns = [
    path('', notification_settings_view, name='notification_settings'),
    path('save-subscription/', save_push_subscription_view, name='save_push_subscription'),
]
