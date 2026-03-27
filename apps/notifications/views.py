from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import NotificationPreferenceForm
from .models import NotificationPreference


@login_required
def notification_settings_view(request):
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            return redirect('notification_settings')
    else:
        form = NotificationPreferenceForm(instance=prefs)

    return render(request, 'notifications/settings.html', {
        'form': form,
    })
