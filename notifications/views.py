from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from .services import *

class AllNotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = PageNumberPagination
    def get(self, request):
        try:
            result = NotificationService.get_notifications(request.user)
            paginator = self.pagination_class()
            paginator.page_size = 10
            paginated_data = paginator.paginate_queryset(result, request)
            
            serializer = self.serializer_class(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        try:
            response = NotificationService.delete_notification(request.user, request.data.get('notification_id'))
            return Response("Notification deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAllNotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        try:
            response = NotificationService.delete_all_notifications(request.user)
            return Response("All notifications deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

