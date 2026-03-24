from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from apps.chat.models import ChatThread
from apps.places.models import Place


@staff_member_required
def dashboard_home_view(request):
    threads = ChatThread.objects.select_related('user', 'assigned_admin').order_by('-updated_at')[:10]
    places_count = Place.objects.count()

    return render(request, 'dashboard/home.html', {
        'threads': threads,
        'places_count': places_count,
    })
