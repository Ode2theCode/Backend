from django.db.models import Count

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter


from django_filters.rest_framework import DjangoFilterBackend


from .serializers import *
from .services import *
from groups.models import*
from .filters import *

class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GroupFilter
    search_fields = ['title']
    ordering_fields = ['title', 'level', 'member_count']
    
    def get(self, request):
        try:
            joined_groups = HomeService.get_joined_groups(request.user, request)
            filtered_groups = self.filter_queryset(joined_groups)
            paginator = self.pagination_class()
            paginator.page_size = 4
            paginated_data = paginator.paginate_queryset(filtered_groups, request)
            serializer = self.serializer_class(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class SuggestionsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuggestionSerializer
    pagination_class = PageNumberPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['title']
    
    def get(self, request):
        try:
            suggestions = SuggestionService.get_suggestions(request.user)
            filtered_suggestions = self.filter_queryset(suggestions)
            paginator = self.pagination_class()
            paginator.page_size = 4
            paginated_data = paginator.paginate_queryset(filtered_suggestions, request)
            serializer = self.serializer_class(paginated_data, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        except Exception:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

class AllGroupsView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = AllGroupsSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GroupFilter
    search_fields = ['title']
    ordering_fields = ['title', 'level', 'member_count']
    
    def get(self, request):
        try:
            groups = AllGroupsService.get_all_groups(request.user)
            groups = groups.annotate(member_count=Count('members'))
            filtered_groups = self.filter_queryset(groups)
            paginator = self.pagination_class()
            paginator.page_size = 4
            paginated_data = paginator.paginate_queryset(filtered_groups, request)
            serializer = self.serializer_class(paginated_data, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        except Exception:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset
    

        
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
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
class UserTimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserTimeSlotSerializer
    
    def get(self, request):
        try:
            time_slots = UserTimeSlotService.get_user_time_slots(request.user)
            serializer = self.serializer_class(time_slots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class UserTimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        try:
            UserTimeSlotService.delete_time_slot(request.user, kwargs.get('id'))
            return Response("time slot deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GroupTimeSlotCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupTimeSlotSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)     
        serializer.is_valid(raise_exception=True)
        try:
            time_slot = GroupTimeSlotService.create_group_time_slot(
                kwargs.get('title'),
                request.user,
                **serializer.validated_data
            )
            return Response(self.serializer_class(time_slot).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GroupTimeSlotListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupTimeSlotSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            time_slots = GroupTimeSlotService.get_group_time_slots(kwargs.get('title'), request.user)
            serializer = self.serializer_class(time_slots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupTimeSlotDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        try:
            GroupTimeSlotService.delete_time_slot(kwargs.get('title'), kwargs.get('id'), request.user)
            return Response("time slot deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
                return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
from django.db import connection
from django.http import JsonResponse

def get_table_data(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM neighborhood")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
    data = [dict(zip(columns, row)) for row in rows]
    return JsonResponse(data, safe=False)
