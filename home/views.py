from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import *
from .services import *
from groups.models import*
from .permissions import *

class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeSerializer
    
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

        
class UserTimeSlotCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = UserTimeSlotSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)     
        serializer.is_valid(raise_exception=True)
        try:
            time_slot = UserTimeSlotService.create_time_slot(
                user=request.user,
                **serializer.validated_data
            )
            return Response(self.serializer_class(time_slot).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class UserTimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = UserTimeSlotSerializer
    
    def get(self, request):
        time_slots = UserTimeSlotService.get_user_time_slots(request.user)
        serializer = self.serializer_class(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserTimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        UserTimeSlotService.delete_time_slot(request.user, kwargs.get('id'))
        return Response("time slot deleted successfully", status=status.HTTP_200_OK)



class GroupTimeSlotCreateView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    serializer_class = GroupTimeSlotSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)     
        serializer.is_valid(raise_exception=True)
        try:
            time_slot = GroupTimeSlotService.create_group_time_slot(
                group=Group.objects.get(title=kwargs.get('title')),
                **serializer.validated_data
            )
            return Response(self.serializer_class(time_slot).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class GroupTimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = GroupTimeSlotSerializer
    
    def get(self, request):
        time_slots = GroupTimeSlotService.get_group_time_slots(request.user)
        serializer = self.serializer_class(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class GroupTimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    def delete(self, request, *args, **kwargs):
        GroupTimeSlotService.delete_group_time_slot(request.user, kwargs.get('id'))
        return Response("time slot deleted successfully", status=status.HTTP_200_OK)
    
    
class SuggestionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = SuggestionSerializer
    
    def get(self, requst):
        suggestions = SuggestionService.get_suggestions(requst.user)
        serializer = self.serializer_class(suggestions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
   
    
from django.db import connection
from django.http import JsonResponse

def get_table_data(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM neighborhood")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
    data = [dict(zip(columns, row)) for row in rows]
    return JsonResponse(data, safe=False)
