from django.urls import path
from .views import landing_view, places_placeholder_view

urlpatterns = [
    path('', landing_view, name='landing'),
    path('places/', places_placeholder_view, name='places_placeholder'),
]
