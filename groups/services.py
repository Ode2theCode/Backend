from rest_framework.exceptions import ValidationError
from rest_framework import status

from groups.models import Group
from authentication.models import User
from chat.models import Chat
from notifications.consumers import NotificationConsumer
from notifications.models import Notification

import boto3

from FD import settings


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class GroupService:
    
    VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    
    @staticmethod
    def delete_s3_object(file_path):
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
        

    def check_title(title):
        if Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group title already exists', 'status': status.HTTP_400_BAD_REQUEST})
        
    def check_level(level):
        if level not in GroupService.VALID_LEVELS:
            raise ValidationError({'detail': f'Invalid level. Please select one of the following: {", ".join(GroupService.VALID_LEVELS)}', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def create_group(cls, user, data):        
        cls.check_level(data.get('level'))
        cls.check_title(data.get('title'))
        group = Group.objects.create(owner=user, **data)
        Chat.objects.create(group=group)
        group.add_member(user)
        return group

    @staticmethod
    def retrieve_group(title, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if not Group.objects.get(title=title).members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'You are not a member of this group', 'status': status.HTTP_403_FORBIDDEN})

        group = Group.objects.get(title=title)
        return group
    
    @staticmethod
    def update_group(title, data, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        
        if group.owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        if 'title' in data and data.get('title') != group.title:
            GroupService.check_title(data.get('title'))
            for member in group.members.all():
                NotificationConsumer.send_notification(member, f"{group.title} has been renamed to {data.get('title')}")
                Notification.objects.create(recipient=member, message=f"{group.title} has been renamed to {data.get('title')}")
            group.title = data.get('title')
            
        if 'description' in data and data.get('description') != group.description:
            for member in group.members.all():
                NotificationConsumer.send_notification(member, f"{member.username} updated the noticeboard of {group.title}")
                Notification.objects.create(recipient=member, message=f"{member.username} updated the noticeboard of {group.title}")
            group.description = data.get('description')
        
        if 'level' in data and data.get('level') != group.level:
            GroupService.check_level(data.get('level'))
            for member in group.members.all():
                NotificationConsumer.send_notification(member, f"{group.title} level has been updated to {data.get('level')}")
                Notification.objects.create(recipient=member, message=f"{group.title} level has been updated to {data.get('level')}")
            group.level = data.get('level')
        
        if not group.image and data.get('image'):
            path = data.get('image').name + f'_{group.id}'
            group.image.save(path, data.get('image'))
        
        if group.image and data.get('image') == '':
            GroupService.delete_s3_object(group.image.name)
            group.image = None
        
        if group.image and data.get('image') and group.image != data.get('image'):
            GroupService.delete_s3_object(group.image.name)
            path = data.get('image').name + f'_{group.id}'
            group.image.save(path, data.get('image'))
            

        group.private = data.get("private", group.private)
        group.meeting_url = data.get("meeting_url", group.meeting_url)
        group.neighborhood = data.get("neighborhood", group.neighborhood)
        group.city = data.get("city", group.city)
        
        group.save()
    
    @classmethod
    def delete_group(cls, title, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        group = Group.objects.get(title=title)
        
        if group.owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        for member in group.members.all():
            NotificationConsumer.send_notification(member, f"{group.title} has been deleted")
            Notification.objects.create(recipient=member, message=f"{group.title} has been deleted")
        if group.image:
            cls.delete_s3_object(group.image.name)

        group.delete()
    
    @staticmethod
    def join_request(title, user):
        group = Group.objects.get(title=title)
        message = ""
        group_status = ""
        
        if group.private:
            if user in group.pending_members.all():
                raise ValidationError({'detail': 'You have already sent a request to join this group', 'status': status.HTTP_400_BAD_REQUEST})
            if user in group.members.all():
                raise ValidationError({'detail': 'You are already a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
            
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
        Notification.objects.create(recipient=group.owner, message=message)
        
        return group_status
    
    def cancel_join_request(title, user):
        group = Group.objects.get(title=title)
        if not group.pending_members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'You have not sent a request to join this group', 'status': status.HTTP_400_BAD_REQUEST})
        
        group.pending_members.remove(user)
    
    @staticmethod
    def pending_requests(title, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        
        if group.owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        return group.pending_members.all()
    
    @staticmethod
    def accept_request(title, username, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if Group.objects.get(title=title).owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if User.objects.get(username=username) not in Group.objects.get(title=title).pending_members.all():
            raise ValidationError({'detail': 'This user has not sent a request to join this group', 'status': status.HTTP_400_BAD_REQUEST})
        
        if User.objects.get(username=username) in Group.objects.get(title=title).members.all():
            raise ValidationError({'detail': 'This user is already a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
        
        user = User.objects.get(username=username)
        group = Group.objects.get(title=title)
        
        
        group.accept_pending_member(user)
        NotificationConsumer.send_notification(user, f"your request to join {group.title} has been accepted")
        Notification.objects.create(recipient=user, message=f"your request to join {group.title} has been accepted")
        
    @staticmethod
    def decline_request(title, username, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if Group.objects.get(title=title).owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if User.objects.get(username=username) not in Group.objects.get(title=title).pending_members.all():
            raise ValidationError({'detail': 'This user has not sent a request to join this group', 'status': status.HTTP_400_BAD_REQUEST})
        
        if User.objects.get(username=username) in Group.objects.get(title=title).members.all():
            raise ValidationError({'detail': 'This user is already a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
        
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
        
        if group.owner == user:
            raise ValidationError({'detail': 'You cannot leave your own group', 'status': status.HTTP_400_BAD_REQUEST})
        

        group.remove_member(user)
        

        group.save()
    
    @staticmethod
    def kick_member(title, username, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if Group.objects.get(title=title).owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        if not User.objects.filter(username=username).exists():
            raise ValidationError({'detail': 'User not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if username == Group.objects.get(title=title).owner.username:
            raise ValidationError({'detail': 'You cannot kik the owner of the group', 'status': status.HTTP_400_BAD_REQUEST})
        
        user = User.objects.get(username=username)
        
        group = Group.objects.get(title=title)
        
        if not group.members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'this user is not a member of this group', 'status': status.HTTP_400_BAD_REQUEST})
        group.remove_member(user)
        group.save()
        
    @staticmethod
    def member_list(title, user):
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        
        if not group.members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'You are not a member of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        return group.members.all()
    
