"""
LCLPD_backend URL Configuration
"""
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="LCLPD API",
        default_version="v1",
        description="API Documentation for LCL Project Digitization",
    ),
    public=False,
)

urlpatterns = [
    url('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', include("user_management.urls")),
    path('inventory/', include("inventory_management.urls")),
    path('market_intelligence/', include("market_intelligence.urls")),
    path('area/', include("area_management.urls")),
    path('channel/', include("channel_management.urls")),
    path('notifications/', include("notifications_management.urls")),
    path('system_logs/', include("system_logs.urls")),
    path('bulk_update/', include("bulk_update_management.urls")),
    path('workflows/', include("workflows.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
