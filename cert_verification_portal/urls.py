from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Keep native django admin on a separate path
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('certificates.urls')),
    path('', include('audit_logs.urls')),
]

# Serve media and static files during local development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
