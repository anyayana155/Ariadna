from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatThread, ChatMessage


@login_required
def open_support_chat_view(request):
    if request.user.is_staff:
        return redirect('admin_chat_list')

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

    if request.method == 'POST':
        text = (request.POST.get('text') or '').strip()

        if text:
            if request.user.is_staff and thread.assigned_admin is None:
                thread.assigned_admin = request.user
                thread.save(update_fields=['assigned_admin', 'updated_at'])

            ChatMessage.objects.create(
                thread=thread,
                sender=request.user,
                text=text
            )

            return redirect('chat_thread', thread_id=thread.id)

    return render(request, 'chat/thread.html', {'thread': thread})


@staff_member_required
def admin_chat_list_view(request):
    threads = ChatThread.objects.select_related('user', 'assigned_admin').order_by('-updated_at')
    return render(request, 'chat/admin_thread_list.html', {'threads': threads})