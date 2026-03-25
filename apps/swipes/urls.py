from django.urls import path
from .views import cards_feed_view, swipe_action_view, liked_places_view

urlpatterns = [
    path('', cards_feed_view, name='cards_feed'),
    path('action/', swipe_action_view, name='swipe_action'),
    path('liked/', liked_places_view, name='liked_places'),
]
