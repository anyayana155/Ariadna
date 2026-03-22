from django.urls import path
from .views import place_detail_view, place_list_view

urlpatterns = [
    path('', place_list_view, name='place_list'),
    path('<slug:slug>/', place_detail_view, name='place_detail'),
]
