from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('trigger_error/', trigger_error),
    path('admin/', admin.site.urls),
    
    path('authentication/', include('authentication.urls')),
    path('groups/', include('groups.urls')),
    path('scheduling/', include('home.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
