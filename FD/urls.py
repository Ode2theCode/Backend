from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django_prometheus import exports
from rest_framework.response import Response
from rest_framework import status

def trigger_error(request):
    division_by_zero = 1 / 0

from rest_framework.decorators import api_view

@api_view(['GET'])
def trigger_400(request):
    return Response("Bad Request", status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def trigger_401(request):
    return Response("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def trigger_403(request):
    return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def trigger_404(request):
    return Response("Not Found", status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def trigger_500(request):
    return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


urlpatterns = [
    path('trigger_error/', trigger_error),
    path('', include('django_prometheus.urls')),

    path('admin/', admin.site.urls),
    
    path('authentication/', include('authentication.urls')),
    path('groups/', include('groups.urls')),
    path('scheduling/', include('home.urls')),
    path('chat/', include('chat.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    path('notifications/', include('notifications.urls')),
    
    path('trigger_400/', trigger_400),
    path('trigger_401/', trigger_401),
    path('trigger_403/', trigger_403),
    path('trigger_404/', trigger_404),
    path('trigger_500/', trigger_500),

]
