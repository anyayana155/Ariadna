from django.urls import path
from .views import save_push_subscription_view

urlpatterns = [
    path('save-subscription/', save_push_subscription_view, name='save_push_subscription'),
]
