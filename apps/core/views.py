from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def landing_view(request):
    return render(request, 'core/landing.html')


@login_required
def places_placeholder_view(request):
    return render(request, 'core/places_placeholder.html')
