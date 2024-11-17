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
        
class TimeSlotCreate(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = TimeSlotCreateSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class TimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = TimeSlotListSerializer
    
    def get(self, request):
        serializer = self.serializer_class(request.user.timeslots.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class TimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = TimeSlotDeleteSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.delete()
            return Response("time slot deleted successfully", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
