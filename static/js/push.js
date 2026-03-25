function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function enablePush() {
    if (!('serviceWorker' in navigator)) {
        throw new Error('Service Worker не поддерживается');
    }

    if (!('PushManager' in window)) {
        throw new Error('PushManager не поддерживается');
    }

    if (!VAPID_PUBLIC_KEY || VAPID_PUBLIC_KEY.length < 80) {
        throw new Error('Некорректный VAPID public key');
    }

    console.log('VAPID_PUBLIC_KEY:', VAPID_PUBLIC_KEY);
    console.log('VAPID_PUBLIC_KEY length:', VAPID_PUBLIC_KEY.length);

    const permission = await Notification.requestPermission();
    console.log('Notification permission:', permission);

    if (permission !== 'granted') {
        throw new Error('Разрешение на уведомления не выдано');
    }

    const registration = await navigator.serviceWorker.register('/static/service-worker.js');
    console.log('Service worker registered:', registration);

    let subscription = await registration.pushManager.getSubscription();
    console.log('Existing subscription:', subscription);

    if (!subscription) {
        const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
        console.log('applicationServerKey length:', applicationServerKey.length);

        subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: applicationServerKey,
        });

        console.log('New subscription created:', subscription);
    }

    const response = await fetch('/notifications/save-subscription/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ subscription }),
    });

    console.log('Save subscription response status:', response.status);

    if (!response.ok) {
        const text = await response.text();
        console.log('Save subscription response body:', text);
        throw new Error(`Ошибка сохранения подписки: ${response.status}`);
    }

    return true;
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('enable-push-btn');

    if (btn) {
        btn.addEventListener('click', async () => {
            try {
                await enablePush();
                alert('Push-уведомления включены для этого устройства.');
            } catch (error) {
                console.error('Push enable error:', error);
                alert(`Не удалось включить push-уведомления: ${error.message}`);
            }
        });
    }
});