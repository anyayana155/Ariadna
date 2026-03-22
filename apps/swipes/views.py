import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.places.models import Place
from .models import SwipeAction


def _get_next_place_for_user(user):
    viewed_ids = SwipeAction.objects.filter(user=user).values_list('place_id', flat=True)

    queryset = Place.objects.filter(is_published=True).exclude(id__in=viewed_ids).prefetch_related('images')

    preferences = getattr(user, 'preferences', None)

    if preferences:
        category_map = {
            'coffee': 'coffee',
            'lunch': 'food',
            'bars': 'bar',
            'walks': 'walk',
            'all': None,
        }

        preferred_category = category_map.get(preferences.purpose)
        if preferred_category:
            preferred_queryset = queryset.filter(category=preferred_category)
            if preferred_queryset.exists():
                queryset = preferred_queryset

    return queryset.first()


def _place_to_json(place):
    images = []
    for image in place.images.all():
        if image.image:
            images.append(image.image.url)
        elif image.external_url:
            images.append(image.external_url)

    return {
        'id': place.id,
        'title': place.title,
        'short_description': place.short_description,
        'full_description': place.full_description,
        'address': place.address,
        'metro': place.metro,
        'average_check': place.average_check,
        'detail_url': f'/places/{place.slug}/',
        'images': images,
    }


@login_required
def cards_feed_view(request):
    place = _get_next_place_for_user(request.user)
    return render(request, 'swipes/cards.html', {'place': place})


@login_required
@require_POST
def swipe_action_view(request):
    try:
        data = json.loads(request.body)
        place_id = data.get('place_id')
        action = data.get('action')

        if action not in ['like', 'dislike', 'skip']:
            return JsonResponse({'error': 'Некорректное действие'}, status=400)

        place = Place.objects.filter(id=place_id, is_published=True).first()
        if not place:
            return JsonResponse({'error': 'Место не найдено'}, status=404)

        SwipeAction.objects.update_or_create(
            user=request.user,
            place=place,
            defaults={'action': action}
        )

        next_place = _get_next_place_for_user(request.user)

        if not next_place:
            return JsonResponse({'done': True})

        return JsonResponse({
            'done': False,
            'next_place': _place_to_json(next_place)
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некорректный JSON'}, status=400)
