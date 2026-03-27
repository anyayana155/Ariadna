from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('preferences/', include('apps.preferences.urls')),
    path('places/', include('apps.places.urls')),
    path('cards/', include('apps.swipes.urls')),
    path('chat/', include('apps.chat.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('favorites/', include('apps.favorites.urls')),
    path('bookings/', include('apps.bookings.urls')),

    re_path(
        r'^service-worker\.js$',
        serve,
        {
            'path': 'service-worker.js',
            'document_root': settings.STATIC_ROOT,
        },
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
