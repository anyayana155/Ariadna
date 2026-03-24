import json

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import NotificationPreferenceForm
from .models import NotificationPreference, PushSubscription


@login_required
@require_POST
def save_push_subscription_view(request):
    data = json.loads(request.body)
    subscription = data.get('subscription', {})
    keys = subscription.get('keys', {})

    endpoint = subscription.get('endpoint')
    p256dh = keys.get('p256dh')
    auth = keys.get('auth')

    if not endpoint or not p256dh or not auth:
        return JsonResponse({'error': 'Некорректная подписка'}, status=400)

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'user': request.user,
            'p256dh_key': p256dh,
            'auth_key': auth,
            'is_active': True,
        }
    )

    return JsonResponse({'status': 'ok'})


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
        'vapid_public_key': settings.VAPID_PUBLIC_KEY,
    })
