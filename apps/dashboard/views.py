from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from openpyxl import Workbook

from apps.bookings.models import BookingRequest
from apps.chat.models import ChatMessage, ChatThread
from apps.dashboard.forms import DashboardBookingUpdateForm, DashboardPlaceForm
from apps.favorites.models import FavoriteFolder
from apps.places.models import Place, PlaceImage
from apps.preferences.models import PreferenceProfile
from apps.swipes.models import SwipeAction


@staff_member_required
def dashboard_home_view(request):
    threads = ChatThread.objects.select_related('user', 'assigned_admin').order_by('-updated_at')[:8]
    bookings = BookingRequest.objects.select_related('user', 'place').order_by('-created_at')[:8]
    places_count = Place.objects.count()
    users_with_preferences = PreferenceProfile.objects.count()

    return render(request, 'dashboard/home.html', {
        'threads': threads,
        'bookings': bookings,
        'places_count': places_count,
        'users_with_preferences': users_with_preferences,
    })


@staff_member_required
def dashboard_bookings_view(request):
    bookings = BookingRequest.objects.select_related('user', 'place').order_by('-created_at')
    return render(request, 'dashboard/bookings.html', {'bookings': bookings})


@staff_member_required
def dashboard_booking_detail_view(request, booking_id):
    booking = get_object_or_404(
        BookingRequest.objects.select_related('user', 'place'),
        id=booking_id
    )

    prefs = getattr(booking.user, 'preferences', None)
    likes = SwipeAction.objects.select_related('place').filter(
        user=booking.user,
        action='like'
    ).order_by('-created_at')[:30]
    dislikes = SwipeAction.objects.select_related('place').filter(
        user=booking.user,
        action='dislike'
    ).order_by('-created_at')[:30]

    if request.method == 'POST':
        form = DashboardBookingUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('dashboard_booking_detail', booking_id=booking.id)
    else:
        form = DashboardBookingUpdateForm(instance=booking)

    return render(request, 'dashboard/booking_detail.html', {
        'booking': booking,
        'form': form,
        'prefs': prefs,
        'likes': likes,
        'dislikes': dislikes,
    })


@staff_member_required
def dashboard_chats_view(request):
    threads = ChatThread.objects.select_related('user', 'assigned_admin').order_by('-updated_at')
    return render(request, 'dashboard/chats.html', {'threads': threads})


@staff_member_required
def dashboard_chat_detail_view(request, thread_id):
    thread = get_object_or_404(
        ChatThread.objects.select_related('user', 'assigned_admin').prefetch_related('messages__sender'),
        id=thread_id
    )

    if request.method == 'POST':
        text = (request.POST.get('text') or '').strip()
        if text:
            if thread.assigned_admin is None:
                thread.assigned_admin = request.user
                thread.save(update_fields=['assigned_admin', 'updated_at'])

            ChatMessage.objects.create(
                thread=thread,
                sender=request.user,
                text=text
            )
            return redirect('dashboard_chat_detail', thread_id=thread.id)

    prefs = getattr(thread.user, 'preferences', None)
    likes = SwipeAction.objects.select_related('place').filter(
        user=thread.user,
        action='like'
    ).order_by('-created_at')[:50]
    dislikes = SwipeAction.objects.select_related('place').filter(
        user=thread.user,
        action='dislike'
    ).order_by('-created_at')[:50]
    folders = FavoriteFolder.objects.filter(user=thread.user).prefetch_related('items__place')

    return render(request, 'dashboard/chat_detail.html', {
        'thread': thread,
        'prefs': prefs,
        'likes': likes,
        'dislikes': dislikes,
        'folders': folders,
    })


@staff_member_required
def dashboard_places_view(request):
    places = Place.objects.prefetch_related('images').order_by('-created_at')
    return render(request, 'dashboard/places.html', {'places': places})


@staff_member_required
def dashboard_place_create_view(request):
    if request.method == 'POST':
        form = DashboardPlaceForm(request.POST, request.FILES)
        if form.is_valid():
            place = form.save(commit=False)
            place.created_by = request.user
            place.save()
            form.save_m2m()

            for image in form.cleaned_data.get('upload_images', []):
                PlaceImage.objects.create(place=place, image=image)

            for url in (form.cleaned_data.get('external_image_urls') or '').splitlines():
                clean_url = url.strip()
                if clean_url:
                    PlaceImage.objects.create(place=place, external_url=clean_url)

            return redirect('dashboard_places')
    else:
        form = DashboardPlaceForm()

    return render(request, 'dashboard/place_form.html', {
        'form': form,
        'page_title': 'Создать место',
        'place': None,
    })


@staff_member_required
def dashboard_place_edit_view(request, place_id):
    place = get_object_or_404(Place.objects.prefetch_related('images'), id=place_id)

    if request.method == 'POST':
        form = DashboardPlaceForm(request.POST, request.FILES, instance=place)
        if form.is_valid():
            place = form.save()

            for image in form.cleaned_data.get('upload_images', []):
                PlaceImage.objects.create(place=place, image=image)

            for url in (form.cleaned_data.get('external_image_urls') or '').splitlines():
                clean_url = url.strip()
                if clean_url:
                    PlaceImage.objects.create(place=place, external_url=clean_url)

            delete_ids = request.POST.getlist('delete_image_ids')
            if delete_ids:
                PlaceImage.objects.filter(place=place, id__in=delete_ids).delete()

            return redirect('dashboard_place_edit', place_id=place.id)
    else:
        form = DashboardPlaceForm(instance=place)

    return render(request, 'dashboard/place_form.html', {
        'form': form,
        'page_title': f'Редактировать: {place.title}',
        'place': place,
    })


@staff_member_required
def dashboard_preferences_view(request):
    profiles = PreferenceProfile.objects.select_related('user').order_by('-updated_at')
    stats = {
        'all': profiles.count(),
        'coffee': profiles.filter(purpose='coffee').count(),
        'lunch': profiles.filter(purpose='lunch').count(),
        'bars': profiles.filter(purpose='bars').count(),
        'walks': profiles.filter(purpose='walks').count(),
        'all_purpose': profiles.filter(purpose='all').count(),
    }

    return render(request, 'dashboard/preferences.html', {
        'profiles': profiles,
        'stats': stats,
    })


@staff_member_required
def dashboard_preferences_export_view(request):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Анкеты'

    headers = [
        'Email',
        'Имя',
        'Бюджет',
        'Атмосфера',
        'Что ищет',
        'С кем гуляет',
        'Расстояние',
        'Дополнительно',
        'Лайков',
        'Дизлайков',
        'Папок',
        'Обновлено',
    ]
    ws.append(headers)

    profiles = PreferenceProfile.objects.select_related('user').order_by('-updated_at')
    for profile in profiles:
        user = profile.user
        likes_count = SwipeAction.objects.filter(user=user, action='like').count()
        dislikes_count = SwipeAction.objects.filter(user=user, action='dislike').count()
        folders_count = FavoriteFolder.objects.filter(user=user).count()

        ws.append([
            user.email,
            user.first_name or getattr(getattr(user, 'profile', None), 'display_name', ''),
            profile.get_budget_display(),
            profile.get_atmosphere_display(),
            profile.get_purpose_display(),
            profile.get_company_type_display(),
            profile.get_distance_display(),
            profile.extra_text or '',
            likes_count,
            dislikes_count,
            folders_count,
            profile.updated_at.strftime('%d.%m.%Y %H:%M'),
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="preferences_export.xlsx"'
    return response
