from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatThread


@login_required
def open_support_chat_view(request):
    if request.user.is_staff:
        return redirect('dashboard_chats')

    thread = ChatThread.objects.filter(user=request.user, is_closed=False).first()

    if not thread:
        thread = ChatThread.objects.create(user=request.user)

    return redirect('chat_thread', thread_id=thread.id)


@login_required
def chat_thread_view(request, thread_id):
    thread = get_object_or_404(
        ChatThread.objects.prefetch_related('messages__sender'),
        id=thread_id
    )

    if not request.user.is_staff and thread.user != request.user:
        return redirect('landing')

    return render(request, 'chat/thread.html', {
        'thread': thread,
        'vapid_public_key': settings.VAPID_PUBLIC_KEY,
    })


@staff_member_required
def admin_chat_list_view(request):
    return redirect('dashboard_chats')
