from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination


from authentication.models import User
from .serializers import *
from .models import *
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
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class GroupRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupRetrieveSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            group = GroupService.retrieve_group(kwargs.get('title'), request.user)
            serializer = self.serializer_class(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class GroupUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def patch(self, request, *args, **kwargs):
        try:
            GroupService.update_group(kwargs.get('title'), request.data, request.user)
            return Response("group updated successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class GroupDeleteView(APIView):  
    permission_classes = [IsAuthenticated]  
    
    def delete(self, request, *args, **kwargs):
        try:
            GroupService.delete_group(kwargs.get('title'), request.user)
            return Response("group deleted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroupJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            type = GroupService.join_request(kwargs.get('title'), request.user)
            if type == "private":
                return Response("request sent successfully", status=status.HTTP_200_OK)
            elif type == "public":
                return Response("you are now a member of this group", status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

     
       
class GroupCancelRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            GroupService.cancel_join_request(kwargs.get('title'), request.user)
            return Response("request cancelled successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  
   
class GroupPendingRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupPendingRequestSerializer
    pagination_class = PageNumberPagination
    
    def get(self, request, *args, **kwargs):
        try:
            group_requests = GroupService.pending_requests(kwargs.get('title'), request.user)
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(group_requests, request)
            serializer = self.serializer_class(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GroupAcceptRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupAcceptRequestSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.accept_request(kwargs.get('title'), serializer.validated_data['username'], request.user)
            return Response("request accepted successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupDeclineRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupDeclineRequestSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.decline_request(kwargs.get('title'), serializer.validated_data['username'], request.user)
            return Response("request declined successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class GroupLeaveView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            GroupService.leave_group(kwargs.get('title'), request.user)
            return Response("group left successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        

class GroupKickView(APIView):
    serializer_class = GroupKickSerializer
    permission_classes = [IsAuthenticated]
    

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            GroupService.kick_member(kwargs.get('title'), serializer.validated_data['username'], request.user)
            return Response("user kicked successfully", status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        except Exception as e:
            return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroupMemberListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupMemberListSerializer
    pagination_class = PageNumberPagination
    

    def get(self, request, *args, **kwargs):
        try:
            print(request.user)
            members = GroupService.member_list(kwargs.get('title'), request.user)
            
            paginator = self.pagination_class()
            paginator.page_size = 4

            paginated_data = paginator.paginate_queryset(members, request)
            serializer = self.serializer_class(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        except ValidationError as e:
            return Response(e.detail.get('detail'), status=e.detail.get('status'))
        # except Exception as e:
        #     return Response("something went wrong. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

