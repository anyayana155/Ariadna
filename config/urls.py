from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('preferences/', include('apps.preferences.urls')),
    path('places/', include('apps.places.urls')),
    path('cards/', include('apps.swipes.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
