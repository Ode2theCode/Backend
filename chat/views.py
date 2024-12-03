# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated

# from .serializers import *
# from .services import *

# class ChatView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ChatSerializer
    
#     def get(self, request, *args, **kwargs):
#         try:
#             messages = ChatService.get_messages(kwargs.get('title'))
#             serializer = self.serializer_class(messages, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except ValidationError as e:
#             return Response(e.detail.get('detail'), status=e.detail.get('status'))
        
#     def post(self, request, *args, **kwargs):
#         try:
#             message = ChatService.send_message(request.user, kwargs.get('title'), request.data['content'])
#             return Response(self.serializer_class(message).data, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             return Response(e.detail.get('detail'), status=e.detail.get('status'))


# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.utils.safestring import mark_safe
# import json

# @login_required
# def chat_room(request, room_name):
#     return render(request, 'chat/room.html', {
#         'room_name_json': mark_safe(json.dumps(room_name))
#     })