from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import *

class HomeView(APIView):
    serializer_class = HomeSerializer
    
    def get(self, request):
        if request.user.is_authenticated:    
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("landing page", status=status.HTTP_200_OK)

