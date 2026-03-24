from django.urls import path
from .views import dashboard_home_view

urlpatterns = [
    path('', dashboard_home_view, name='dashboard_home'),
]
