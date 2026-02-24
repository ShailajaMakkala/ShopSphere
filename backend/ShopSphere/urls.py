from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # JWT Token Refresh (used by frontend auto-refresh interceptor)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/finance/', include('finance.api_urls')),
    path('api/vendor/', include('vendor.api_urls')),
    path('api/delivery/', include('deliveryAgent.api_urls')),

    # Django Admin
    path('admin/', admin.site.urls),
    
    # Template-based views for each app
    path('vendor/', include('vendor.urls')),
    path('superAdmin/', include('superAdmin.urls')),
    path('deliveryAgent/', include('deliveryAgent.urls')),
    path('adminapp/', include('admin.urls')),
    
    # Main site URLs (Keep at the bottom)
    path('', include('user.urls')),
]

# Serve media files (only in development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
