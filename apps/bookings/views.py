from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.places.models import Place
from .forms import BookingRequestForm
from .models import BookingRequest


@login_required
def booking_create_view(request, place_id):
    place = get_object_or_404(Place, id=place_id, is_published=True)

    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.place = place
            booking.save()
            return redirect('booking_detail', booking_id=booking.id)
    else:
        initial = {}
        if request.user.first_name:
            initial['name'] = request.user.first_name
        form = BookingRequestForm(initial=initial)

    return render(request, 'bookings/create.html', {
        'form': form,
        'place': place,
    })


@login_required
def my_booking_requests_view(request):
    requests_qs = BookingRequest.objects.select_related('place').filter(user=request.user)
    return render(request, 'bookings/my_requests.html', {
        'requests': requests_qs,
    })


@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(
        BookingRequest.objects.select_related('place'),
        id=booking_id,
        user=request.user
    )
    return render(request, 'bookings/detail.html', {'booking': booking})