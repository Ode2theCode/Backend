from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import *
from .models import *
from .permissions import *


class GroupCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = GroupCreateSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupRetrieveView(APIView):
    serializer_class = GroupRetrieveSerializer
    
    def get(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            group = Group.objects.get(title=kwargs.get('title'))
            serializer = self.serializer_class(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)


class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    serializer_class = GroupUpdateSerializer
    
    def patch(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            group = Group.objects.get(title=kwargs.get('title'))
            serializer = self.serializer_class(
                group, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.update(group, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)


class GroupDeleteView(APIView):  
    permission_classes = [IsAuthenticated, IsGroupOwner]  
    def delete(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            if request.user.owned_groups.filter(title=kwargs.get('title')).exists():
                group = Group.objects.get(title=kwargs.get('title'))
                group.delete()
                return Response("group deleted successfully", status=status.HTTP_200_OK)
            else:
                return Response("you are not the owner of this group", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)
        

class GroupJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            group = Group.objects.get(title=kwargs.get('title'))
            if group.max_members < group.members.count():
                return Response("group is full", status=status.HTTP_400_BAD_REQUEST)
            if group.level != request.user.level:
                return Response(f"your level is not compatible with this group your level is {request.user.level} and group level is {group.level}", status=status.HTTP_400_BAD_REQUEST)
            
            if group.private:
                group.add_pending_member(request.user)
                return Response("join request sent successfully", status=status.HTTP_200_OK)
            else:
                group.add_member(request.user)
                return Response("you are now a member of this group", status=status.HTTP_200_OK)
            
class GroupPendingRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    def get(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            group = Group.objects.get(title=kwargs.get('title'))
            serializer = GroupPendingRequestSerializer(group.pending_members.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)

class GroupAcceptRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    def post(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            group = Group.objects.get(title=kwargs.get('title'))
            group.accept_pending_member(request.user)
            return Response("request accepted successfully", status=status.HTTP_200_OK)
        else:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)
        
class GroupDeclineRequestView(APIView):
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    def post(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            group = Group.objects.get(title=kwargs.get('title'))
            group.remove_pending_member(request.user)
            return Response("request declined successfully", status=status.HTTP_200_OK)
        else:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)
        

class GroupLeaveView(APIView):
    permission_classes = [IsAuthenticated, IsGroupMember]
    def post(self, request, *args, **kwargs):
        if Group.objects.filter(title=kwargs.get('title')).exists():
            group = Group.objects.get(title=kwargs.get('title'))
            group.remove_member(request.user)
            return Response("you left the group successfully", status=status.HTTP_200_OK)
        else:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)