from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from silk.profiling.profiler import silk_profile

from authentication.models import User
from .serializers import *
from .models import *
from .permissions import *
from .services import *



class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupCreateSerializer
    
    @silk_profile(name='group-create')
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            GroupService.create_group(request.user, serializer.validated_data)
            return Response("group created successfully", status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        

class GroupRetrieveView(APIView):
    serializer_class = GroupRetrieveSerializer
    
    @silk_profile(name='group-retrieve')
    def get(self, request, *args, **kwargs):
        try:
            group = GroupService.retrieve_group(kwargs.get('title'))
            serializer = self.serializer_class(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))



class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    @silk_profile(name='group-update')
    def patch(self, request, *args, **kwargs):
        try:
            GroupService.update_group(kwargs.get('title'), request.data)
            return Response("group updated successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))



class GroupDeleteView(APIView):  
    permission_classes = [IsAuthenticated, IsGroupOwner]  
    
    @silk_profile(name='group-delete')
    def delete(self, request, *args, **kwargs):
        try:
            GroupService.delete_group(kwargs.get('title'))
            return Response("group deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
    

class GroupJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    @silk_profile(name='group-join-request')
    def post(self, request, *args, **kwargs):
        try:
            type = GroupService.join_request(kwargs.get('title'), request.user)
            if type == "private":
                return Response("request sent successfully", status=status.HTTP_200_OK)
            elif type == "public":
                return Response("you are now a member of this group", status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
     
       
class GroupCancelRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    @silk_profile(name='group-join-request-cancel')
    def post(self, request, *args, **kwargs):
        try:
            GroupService.cancel_join_request(kwargs.get('title'), request.user)
            return Response("request cancelled successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
  
   
class GroupPendingRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    serializer_class = GroupPendingRequestSerializer
    pagination_class = PageNumberPagination
    
    @silk_profile(name='group-pending-request')
    def get(self, request, *args, **kwargs):
        try:
            group_requests = GroupService.pending_requests(kwargs.get('title'))
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(group_requests, request)
            serializer = self.serializer_class(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))


class GroupAcceptRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    serializer_class = GroupAcceptRequestSerializer
    
    @silk_profile(name='group-accept-request')
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.accept_request(kwargs.get('title'), serializer.validated_data['username'])
            return Response("request accepted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))


class GroupDeclineRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    serializer_class = GroupDeclineRequestSerializer
    
    @silk_profile(name='group-decline-request')
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.decline_request(kwargs.get('title'), serializer.validated_data['username'])
            return Response("request accepted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))


class GroupLeaveView(APIView):
    permission_classes = [IsAuthenticated, IsGroupMember]
    
    @silk_profile(name='group-leave')
    def post(self, request, *args, **kwargs):
        try:
            GroupService.leave_group(kwargs.get('title'), request.user)
            return Response("group left successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))

        

class GroupKickView(APIView):
    serializer_class = GroupKickSerializer
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    
    @silk_profile(name='group-kick-member')
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.kick_member(kwargs.get('title'), serializer.validated_data['username'])
            return Response("user kicked successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        

class GroupMemberListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupMemberListSerializer
    pagination_class = PageNumberPagination
    
    
    @silk_profile(name='group-member-list')
    def get(self, request, *args, **kwargs):
        try:
            members = GroupService.member_list(kwargs.get('title'))
            
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(members, request)
            serializer = self.serializer_class(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))