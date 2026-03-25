from django.urls import path

from .views import (
    dashboard_booking_detail_view,
    dashboard_bookings_view,
    dashboard_chat_detail_view,
    dashboard_chats_view,
    dashboard_home_view,
    dashboard_place_create_view,
    dashboard_place_delete_view,
    dashboard_place_edit_view,
    dashboard_places_view,
    dashboard_preferences_export_view,
    dashboard_preferences_view,
)

urlpatterns = [
    path('', dashboard_home_view, name='dashboard_home'),
    path('bookings/', dashboard_bookings_view, name='dashboard_bookings'),
    path('bookings/<int:booking_id>/', dashboard_booking_detail_view, name='dashboard_booking_detail'),
    path('chats/', dashboard_chats_view, name='dashboard_chats'),
    path('chats/<int:thread_id>/', dashboard_chat_detail_view, name='dashboard_chat_detail'),
    path('places/', dashboard_places_view, name='dashboard_places'),
    path('places/create/', dashboard_place_create_view, name='dashboard_place_create'),
    path('places/<int:place_id>/edit/', dashboard_place_edit_view, name='dashboard_place_edit'),
    path('places/<int:place_id>/delete/', dashboard_place_delete_view, name='dashboard_place_delete'),
    path('preferences/', dashboard_preferences_view, name='dashboard_preferences'),
    path('preferences/export/', dashboard_preferences_export_view, name='dashboard_preferences_export'),
]
