from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import *
from .services import *
from groups.models import*
from .permissions import *

class HomeView(APIView):
    serializer_class = HomeSerializer
    
    def get(self, request):
        if request.user.is_authenticated:    
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("landing page", status=status.HTTP_200_OK)
        
class TimeSlotCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = TimeSlotSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)     
        serializer.is_valid(raise_exception=True)
        try:
            time_slot = TimeSlotService.create_time_slot(
                user=request.user,
                **serializer.validated_data
            )
            return Response(self.serializer_class(time_slot).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class TimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = TimeSlotSerializer
    
    def get(self, request):
        time_slots = TimeSlotService.get_user_time_slots(request.user)
        serializer = self.serializer_class(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class TimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        TimeSlotService.delete_time_slot(request.user, kwargs.get('id'))
        return Response("time slot deleted successfully", status=status.HTTP_200_OK)



class GroupTimeSlotCreateView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    serializer_class = TimeSlotSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)     
        serializer.is_valid(raise_exception=True)
        try:
            time_slot = TimeSlotService.create_group_time_slot(
                group=Group.objects.get(title=kwargs.get('title')),
                **serializer.validated_data
            )
            return Response(self.serializer_class(time_slot).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class GroupTimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = TimeSlotSerializer
    
    def get(self, request):
        time_slots = TimeSlotService.get_group_time_slots(request.user)
        serializer = self.serializer_class(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class GroupTimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    def delete(self, request, *args, **kwargs):
        TimeSlotService.delete_group_time_slot(request.user, kwargs.get('id'))
        return Response("time slot deleted successfully", status=status.HTTP_200_OK)
    
    
class SuggestionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = SuggestionSerializer
    
    def get(self, requst):
        suggestions = SuggestionService.get_suggestions(requst.user)
        serializer = self.serializer_class(suggestions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)