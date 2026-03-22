from django.shortcuts import get_object_or_404, render
from .models import Place


def place_list_view(request):
    places = Place.objects.filter(is_published=True).prefetch_related('images')
    return render(request, 'places/list.html', {'places': places})


def place_detail_view(request, slug):
    place = get_object_or_404(
        Place.objects.prefetch_related('images', 'tags'),
        slug=slug,
        is_published=True
    )
    return render(request, 'places/detail.html', {'place': place})
