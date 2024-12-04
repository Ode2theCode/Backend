from rest_framework.exceptions import ValidationError
from rest_framework import status

from groups.models import Group
from authentication.models import User
from chat.models import Chat
from notifications.consumers import NotificationConsumer
from notifications.models import Notification

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class GroupService:
    
    VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    
    def check_title(title):
        if Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group title already exists', 'status': status.HTTP_400_BAD_REQUEST})
        
    def check_level(level):
        if level not in GroupService.VALID_LEVELS:
            raise ValidationError({'detail': f'Invalid level. Please select one of the following: {", ".join(Group.VALID_LEVELS)}', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def create_group(cls, user, data):        
        cls.check_title(data.get('title'))
        group = Group.objects.create(owner=user, **data)
        Chat.objects.create(group=group)
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
        
        if 'title' in data and data.get('title') != group.title:
            GroupService.check_title(data.get('title'))
            for member in group.members.all():
                NotificationConsumer.send_notification(member, f"{group.title} has been renamed to {data.get('title')}")
            group.title = data.get('title')
            
        if 'description' in data and data.get('description') != group.description:
            for member in group.members.all():
                NotificationConsumer.send_notification(member, f"{member.username} updated the description of {group.title}")
            group.description = data.get('description')
        
        if 'level' in data and data.get('level') != group.level:
            GroupService.check_level(data.get('level'))
            for member in group.members.all():
                NotificationConsumer.send_notification(member, f"{group.title} level has been updated to {data.get('level')}")
            group.level = data.get('level')
        
        group.image = data.get("image", group.image)
        group.private = data.get("private", group.private)
        group.meeting_url = data.get("meeting_url", group.meeting_url)
        group.neighborhood = data.get("neighborhood", group.neighborhood)
        group.city = data.get("city", group.city)
        
        group.save()
    
    @staticmethod
    def delete_group(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        group = Group.objects.get(title=title)
        group.delete()
    
    @staticmethod
    def join_request(title, user):
        group = Group.objects.get(title=title)
        message = ""
        group_status = ""
        
        if group.private:
            if user in group.pending_members.all():
                raise ValidationError({'detail': 'You have already sent a request to join this group', 'status': status.HTTP_400_BAD_REQUEST})
            
            group.add_pending_member(user)            
            group_status = "private"
            message = f"{user.username} wants to join {group.title}"
        else:
            if user in group.members.all():
                raise ValidationError({'detail': 'You are already a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
            group.add_member(user)
            
            group_status = "public"
            message = f"{user.username} joined {group.title}"
            
        NotificationConsumer.send_notification(group.owner, message)
        
        return group_status
    
    def cancel_join_request(title, user):
        group = Group.objects.get(title=title)
        if not group.pending_members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'You have not sent a request to join this group', 'status': status.HTTP_400_BAD_REQUEST})
        
        group.pending_members.remove(user)
    
    @staticmethod
    def pending_requests(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        return group.pending_members.all()
    
    @staticmethod
    def accept_request(title, username):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        user = User.objects.get(username=username)
        group = Group.objects.get(title=title)
        group.accept_pending_member(user)
        NotificationConsumer.send_notification(user, f"your request to join {group.title} has been accepted")
        
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
        if not group.members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'this user is not a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
        group.remove_member(user)
        group.save()
        
    @staticmethod
    def member_list(title):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        return group.members.all()
    
