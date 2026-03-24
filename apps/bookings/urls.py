from django.urls import path
from .views import booking_create_view, my_booking_requests_view, booking_detail_view

urlpatterns = [
    path('create/<int:place_id>/', booking_create_view, name='booking_create'),
    path('my/', my_booking_requests_view, name='my_booking_requests'),
    path('<int:booking_id>/', booking_detail_view, name='booking_detail'),
]
