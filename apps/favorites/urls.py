from django.urls import path
from .views import (
    add_to_folder_modal_view,
    add_to_folder_view,
    create_folder_view,
    folder_detail_view,
    folders_list_view,
    remove_from_folder_view,
)

urlpatterns = [
    path('', folders_list_view, name='favorite_folders'),
    path('folders/<int:folder_id>/', folder_detail_view, name='favorite_folder_detail'),
    path('create/', create_folder_view, name='favorite_folder_create'),
    path('add/<int:place_id>/', add_to_folder_view, name='favorite_add_to_folder'),
    path('add-form/<int:place_id>/', add_to_folder_modal_view, name='favorite_add_to_folder_form'),
    path('remove/<int:item_id>/', remove_from_folder_view, name='favorite_remove_from_folder'),
]
