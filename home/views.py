from django.db.models import Count

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter


from django_filters.rest_framework import DjangoFilterBackend
from silk.profiling.profiler import silk_profile

from .serializers import *
from .services import *
from groups.models import*
from .permissions import *
from .filters import *

class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeSerializer
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['title']
    
    @silk_profile(name='my-groups')
    def get(self, request):
        joined_groups = HomeService.get_joined_groups(request.user, request)
        filtered_groups = self.filter_queryset(joined_groups)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(filtered_groups, request)
        serializer = self.serializer_class(paginated_data, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class SuggestionsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuggestionSerializer
    pagination_class = PageNumberPagination
    
    @silk_profile(name='suggestions')
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GroupFilter
    search_fields = ['title']
    ordering_fields = ['level', 'member_count']
    
    @silk_profile(name='all-groups')
    def get(self, request):
        groups = AllGroupsService.get_all_groups()
        groups = groups.annotate(member_count=Count('members'))
        filtered_groups = self.filter_queryset(groups)
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(filtered_groups, request)
        serializer = self.serializer_class(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset
    

        
class UserTimeSlotCreateView(APIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = UserTimeSlotSerializer
    
    @silk_profile(name='create-user-time-slot')
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
    
    @silk_profile(name='user-time-slots-retrieve')
    def get(self, request):
        time_slots = UserTimeSlotService.get_user_time_slots(request.user)
        serializer = self.serializer_class(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserTimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    @silk_profile(name='user-time-slot-delete')
    def delete(self, request, *args, **kwargs):
        try:
            UserTimeSlotService.delete_time_slot(request.user, kwargs.get('id'))
            return Response("time slot deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))




class GroupTimeSlotCreateView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    serializer_class = GroupTimeSlotSerializer
    
    @silk_profile(name='create-group-time-slot')
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
    
    @silk_profile(name='group-time-slots-retrieve')
    def get(self, request, *args, **kwargs):
        try:
            time_slots = GroupTimeSlotService.get_group_time_slots(kwargs.get('title'))
            serializer = self.serializer_class(time_slots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
    

class GroupTimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    @silk_profile(name='group-time-slot-delete')
    def delete(self, request, *args, **kwargs):
        try:
            GroupTimeSlotService.delete_time_slot(kwargs.get('title'), kwargs.get('id'))
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
