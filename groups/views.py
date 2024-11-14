from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .models import *


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class GroupView(APIView):
    serializer_class = GroupSerializer
    
    def post(self, request):
        """Create a new group"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, title=None):
        """Retrieve a group or list all groups"""
        if title:
            try:
                group = Group.objects.get(title=title)
                serializer = self.serializer_class(group)
                return Response(serializer.data)
            except Group.DoesNotExist:
                return Response("group not found", status=status.HTTP_404_NOT_FOUND)
        
        groups = Group.objects.all()
        serializer = self.serializer_class(groups, many=True)
        return Response(serializer.data)
    
    def patch(self, request, title):
        """Update a group partially"""
        try:
            group = Group.objects.get(title=title)
            serializer = self.serializer_class(
                group, 
                data=request.data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Group.DoesNotExist:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, title):
        """Delete a group"""
        try:
            group = Group.objects.get(title=title)
            group.delete()
            return Response("group deleted successfully", status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response("group not found", status=status.HTTP_404_NOT_FOUND)















# class GroupCreateView(APIView):
#     serializer_class = GroupSerializer
    
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
        
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# class GroupRetriveView(APIView):
#     serializer_class = GroupSerializer
    
#     def get(self, request, *args, **kwargs):
#         title = kwargs.get('title')
#         try:
#             group = Group.objects.get(title=title)
#             serializer = self.serializer_class(group)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Group.DoesNotExist:
#             return Response("group not found", status=status.HTTP_404_NOT_FOUND)
        
# class GroupDeleteView(APIView):
#     serializer_class = GroupSerializer
    
#     def delete(self, request, *args, **kwargs):
#         title = kwargs.get('title')
#         try:
#             group = Group.objects.get(title=title)
#             serializer = self.serializer_class(group)
#             serializer.delete(group)
#             return Response("group deleted successfully", status=status.HTTP_200_OK)
#         except Group.DoesNotExist:
#             return Response("group not found", status=status.HTTP_404_NOT_FOUND)
        

# class GroupUpdateView(APIView):
#     serializer_class = GroupUpdateSerializer
    
#     def patch(self, request, *args, **kwargs):
#         title = kwargs.get('title')
#         try:
#             group = Group.objects.get(title=title)
#             serializer = self.serializer_class(group, data=request.data, partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Group.DoesNotExist:
#             raise Response("group not found", status=status.HTTP_404_NOT_FOUND)