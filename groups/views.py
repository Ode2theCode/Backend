from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


from authentication.models import User
from .serializers import *
from .models import *
from .permissions import *
from .services import *


class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupCreateSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            GroupService.create_group(request.user, serializer.validated_data)
            return Response("group created successfully", status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        


class GroupRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupRetrieveSerializer
    
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
    serializer_class = GroupUpdateSerializer
    
    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.update_group(kwargs.get('title'), serializer.validated_data)
            return Response("group updated successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))

class GroupDeleteView(APIView):  
    permission_classes = [IsAuthenticated, IsGroupOwner]  
    def delete(self, request, *args, **kwargs):
        try:
            GroupService.delete_group(kwargs.get('title'))
            return Response("group deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        


class GroupJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            GroupService.join_request(kwargs.get('title'), request.user)
            return Response("request sent successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
     
class GroupPendingRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    serializer_class = GroupPendingRequestSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            group = GroupService.pending_requests(kwargs.get('title'))
            serializer = self.serializer_class(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))


class GroupAcceptRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    serializer_class = GroupAcceptRequestSerializer
    
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
    
    def post(self, request, *args, **kwargs):
        try:
            GroupService.leave_group(kwargs.get('title'), request.user)
            return Response("group left successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        

class GroupKickView(APIView):
    serializer_class = GroupKickSerializer
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.kick_user(kwargs.get('title'), serializer.validated_data['username'])
            return Response("user kicked successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        