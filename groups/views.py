from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .models import *


class GroupCreateView(APIView):
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