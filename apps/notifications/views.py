import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import PushSubscription


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