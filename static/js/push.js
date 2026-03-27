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

function waitForActiveServiceWorker(registration) {
    return new Promise((resolve, reject) => {
        if (registration.active) {
            resolve(registration);
            return;
        }

        const worker = registration.installing || registration.waiting;
        if (!worker) {
            resolve(registration);
            return;
        }

        worker.addEventListener('statechange', () => {
            if (worker.state === 'activated') {
                resolve(registration);
            }
        });

        setTimeout(() => reject(new Error('Service Worker activation timeout')), 10000);
    });
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

    console.log('User agent:', navigator.userAgent);
    console.log('Notification.permission before request:', Notification.permission);

    let permission = Notification.permission;
    if (permission === 'default') {
        permission = await Notification.requestPermission();
    }

    console.log('Notification permission:', permission);

    if (permission !== 'granted') {
        throw new Error('Разрешение на уведомления не выдано');
    }

    const registration = await navigator.serviceWorker.register('/service-worker.js', {
        scope: '/',
        updateViaCache: 'none',
    });

    await waitForActiveServiceWorker(registration);
    await navigator.serviceWorker.ready;

    console.log('Service worker registered:', registration);

    const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
    console.log('applicationServerKey length:', applicationServerKey.length);

    let subscription = await registration.pushManager.getSubscription();
    console.log('Existing subscription:', subscription);

    if (subscription) {
        try {
            await subscription.unsubscribe();
            console.log('Old subscription removed');
        } catch (e) {
            console.warn('Failed to unsubscribe old subscription:', e);
        }
        subscription = null;
    }

    try {
        if (registration.pushManager.permissionState) {
            const state = await registration.pushManager.permissionState({
                userVisibleOnly: true,
                applicationServerKey,
            });
            console.log('Push permissionState:', state);
        }
    } catch (e) {
        console.warn('permissionState check failed:', e);
    }

    subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey,
    });

    console.log('New subscription created:', subscription);

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
                console.error('Push enable error name:', error?.name);
                console.error('Push enable error message:', error?.message);
                alert(`Не удалось включить push-уведомления: ${error.message}`);
            }
        });
    }
});
