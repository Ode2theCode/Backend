from rest_framework.permissions import BasePermission
from groups.models import *

class IsGroupOwner(BasePermission):
    def has_permission(self, request, view, obj):
        group_title = view.kwargs.get('title')

        group = Group.objects.get(title=group_title)
    
class IsGroupMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.members.all()