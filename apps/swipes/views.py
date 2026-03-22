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
            matching = queryset.filter(category=preferred_category)
            if matching.exists():
                queryset = matching

    return queryset.first()


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

        first_image = next_place.images.first()

        return JsonResponse({
            'done': False,
            'next_place': {
                'id': next_place.id,
                'title': next_place.title,
                'short_description': next_place.short_description,
                'address': next_place.address,
                'average_check': next_place.average_check,
                'detail_url': f'/places/{next_place.slug}/',
                'image_url': first_image.image.url if first_image and first_image.image else (
                    first_image.external_url if first_image else ''
                )
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некорректный JSON'}, status=400)