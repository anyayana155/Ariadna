from django.urls import path
from .views import open_support_chat_view, chat_thread_view, admin_chat_list_view

urlpatterns = [
    path('open/', open_support_chat_view, name='open_support_chat'),
    path('admin/list/', admin_chat_list_view, name='admin_chat_list'),
    path('<int:thread_id>/', chat_thread_view, name='chat_thread'),
]