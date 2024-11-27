from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend


from .serializers import *
from .services import *
from groups.models import*
from .permissions import *
from .filters import *

class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeSerializer
    pagination_class = PageNumberPagination
    
    def get(self, request):
        joined_groups = HomeService.get_joined_groups(request.user)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(joined_groups, request)
        serializer = self.serializer_class(paginated_data, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class SuggestionsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuggestionSerializer
    pagination_class = PageNumberPagination
    
    def get(self, request):
        suggestions = SuggestionService.get_suggestions(request.user)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(suggestions, request)
        serializer = self.serializer_class(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class AllGroupsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    
    def get(self, request):
        groups = AllGroupsService.get_all_groups(request)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(groups, request)
        serializer = self.serializer_class(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
    

        
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
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        
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
        try:
            UserTimeSlotService.delete_time_slot(request.user, kwargs.get('id'))
            return Response("time slot deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))



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
            return Response(e.detail.get('detail'), status=e.detail.get('status'))


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
        try:
            GroupTimeSlotService.delete_group_time_slot(request.user, kwargs.get('id'))
            return Response("time slot deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
       
    
from django.db import connection
from django.http import JsonResponse

def get_table_data(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM neighborhood")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
    data = [dict(zip(columns, row)) for row in rows]
    return JsonResponse(data, safe=False)
