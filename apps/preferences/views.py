from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PreferenceProfileForm
from .models import PreferenceProfile


@login_required
def preference_create_or_update_view(request):
    preference, created = PreferenceProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PreferenceProfileForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('cards_feed')
    else:
        form = PreferenceProfileForm(instance=preference)

    return render(request, 'preferences/form.html', {
        'form': form,
        'is_edit': not created
    })


@login_required
def preference_edit_view(request):
    preference, _ = PreferenceProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PreferenceProfileForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PreferenceProfileForm(instance=preference)

    return render(request, 'preferences/form.html', {
        'form': form,
        'is_edit': True
    })