from rest_framework.exceptions import ValidationError
from rest_framework import status

from groups.models import Group
from authentication.models import User


class GroupService:
    
    def check_title(title):
        if Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group title already exists', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def create_group(cls, user, data):        
        cls.check_title(data.get('title'))
        group = Group.objects.create(owner=user, **data)
        group.add_member(user)
        return group

    @staticmethod
    def retrieve_group(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})

        group = Group.objects.get(title=title)
        return group
    
    @staticmethod
    def update_group(title, data):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        group.description = data.get('description', group.description)
        group.image = data.get('image', group.image)
        group.level = data.get('level', group.level)
        group.city = data.get('city', group.city)
        group.neighborhood = data.get('neighborhood', group.neighborhood)
        group.meeting_url = data.get('meeting_url', group.meeting_url)
        group.private = data.get('private', group.private)
        group.save()
        return group
    
    @staticmethod
    def delete_group(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        group = Group.objects.get(title=title)
        group.delete()
    
    @staticmethod
    def join_request(title, user):
        group = Group.objects.get(title=title)
        if user.level != group.level:
            raise ValidationError({'detail': 'Your level does not match the group level', 'status': status.HTTP_400_BAD_REQUEST})
        
        if group.private:
            group.add_pending_member(user)
            return "private"
        else:
            group.add_member(user)
            return "public"
    
    @staticmethod
    def pending_requests(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        return group
    
    @staticmethod
    def accept_request(title, username):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        user = User.objects.get(username=username)
        group = Group.objects.get(title=title)
        group.accept_pending_member(user)
        
    @staticmethod
    def decline_request(title, username):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        user = User.objects.get(username=username)
        group = Group.objects.get(title=title)
        group.decline_pending_member(user)
    
    @staticmethod
    def leave_group(title, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        if not group.members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'You are not a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
        group.remove_member(user)
        
        if group.owner == user:
            group.delete()
        group.save()
    
    @staticmethod
    def kik_member(title, username):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        user = User.objects.get(username=username)
        
        group = Group.objects.get(title=title)
        if not group.members.filter(username=username).exists():
            raise ValidationError({'detail': 'You are not a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
        group.remove_member(user)
        group.save()
        
    @staticmethod
    def member_list(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        return group.members.all()
    
