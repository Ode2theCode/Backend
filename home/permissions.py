from rest_framework.permissions import BasePermission

class IsGroupOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    
class IsGroupMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.members.all()