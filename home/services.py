import redis
from dotenv import load_dotenv
import os
from groups.models import Group

load_dotenv()

redis_url = os.getenv('REDIS_URL')
redis_client = redis.StrictRedis.from_url(redis_url)

from django.db.models import QuerySet, Q

from rest_framework.exceptions import ValidationError
from rest_framework import status

from .models import *
from groups.models import *

from .filters import GroupFilter

class UserTimeSlotService:
    @staticmethod
    def validate_time_range(start_time: float, end_time: float) -> None:
        if not (0 <= start_time <= 24 and 0 <= end_time <= 24):
            raise ValidationError({'detail': 'Time must be between 0 and 24', 'status': status.HTTP_400_BAD_REQUEST})
            
        if end_time <= start_time:
            raise ValidationError({'detail': 'End time must be after start time', 'status': status.HTTP_400_BAD_REQUEST})


    @staticmethod
    def validate_overlap(user, day_of_week: str, start_time: float, end_time: float) -> None:
        
        overlapping = UserTimeSlot.objects.filter(
            user=user,
            day_of_week=day_of_week.lower(),
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        if overlapping.exists():
            raise ValidationError({'detail': 'This time slot overlaps with an existing slot', 'status': status.HTTP_400_BAD_REQUEST})


    @classmethod
    def create_time_slot(cls, user, day_of_week: str, start_time: float, end_time: float) -> UserTimeSlot:
        
        cls.validate_time_range(start_time, end_time)
        cls.validate_overlap(user, day_of_week, start_time, end_time)
        
        time_slot = UserTimeSlot.objects.create(
            user=user,
            day_of_week=day_of_week.lower(),
            start_time=start_time,
            end_time=end_time
        )

        return time_slot
    
    def get_user_time_slots(user) -> QuerySet[UserTimeSlot]:
        return UserTimeSlot.objects.filter(user=user)
    
    @staticmethod
    def delete_time_slot(user, time_slot_id: int) -> None:
        time_slot = UserTimeSlot.objects.filter(
            id=time_slot_id,
            user=user
        ).first()
        
        if not time_slot:
            raise ValidationError({'detail': 'Time slot not found', 'status': status.HTTP_404_NOT_FOUND})

            
        time_slot.delete()
    
    
    
class GroupTimeSlotService:
    @staticmethod
    def validate_time_range(start_time: float, end_time: float) -> None:
        if not (0 <= start_time <= 24 and 0 <= end_time <= 24):
            raise ValidationError({'detail': 'Time must be between 0 and 24', 'status': status.HTTP_400_BAD_REQUEST})
            
        if end_time <= start_time:
            raise ValidationError({'detail': 'End time must be after start time', 'status': status.HTTP_400_BAD_REQUEST})

    @staticmethod
    def validate_overlap(group, day_of_week: str, start_time: float, end_time: float) -> None:
        
        overlapping = GroupTimeSlot.objects.filter(
            group=group,
            day_of_week=day_of_week.lower(),
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        if overlapping.exists():
            raise ValidationError({'detail': 'This time slot overlaps with an existing slot', 'status': status.HTTP_400_BAD_REQUEST})


    @classmethod
    def create_group_time_slot(cls, group, day_of_week: str, start_time: float, end_time: float) -> GroupTimeSlot:
        
        cls.validate_time_range(start_time, end_time)
        cls.validate_overlap(group, day_of_week, start_time, end_time)
        
        time_slot = GroupTimeSlot.objects.create(
            group=group,
            day_of_week=day_of_week.lower(),
            start_time=start_time,
            end_time=end_time
        )

        return time_slot
        
    def get_group_time_slots(title) -> QuerySet[GroupTimeSlot]:
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        group = Group.objects.get(title=title)
        return group.time_slots.all()
    
    @staticmethod
    def delete_time_slot(title, time_slot_id: int) -> None:
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        group = Group.objects.get(title=title)
        if not group.time_slots.filter(id=time_slot_id).exists():
            raise ValidationError({'detail': 'Time slot not found', 'status': status.HTTP_404_NOT_FOUND})
        time_slot = group.time_slots.filter(id=time_slot_id).first()
        time_slot.delete()
    
    
    
class HomeService:
    def get_joined_groups(user, request) -> list[Group]:
        queryset = Group.objects.filter(members=user)
        
        search_term = request.GET.get('search')
        if search_term:
            queryset = queryset.filter(title__icontains=search_term)
        
        return queryset

    
class SuggestionService:
    

    def get_suggestions(user) -> list[Group]:
        cached_groups = redis_client.get(f'user:{user.id}:matching_groups')
        
        if cached_groups:
            print("Using cached groups")
            group_ids = cached_groups.decode('utf-8').split(',')
            return Group.objects.filter(id__in=group_ids)
        
        print("Not using cached groups")
        
        loc = user.neighborhood if user.neighborhood else None
        user_time_slots = UserTimeSlotService.get_user_time_slots(user)
        
        groups = Group.objects.all().prefetch_related('time_slots', 'members')
        group_matches = []
        
        for group in groups:
            group_time_slots = group.time_slots.all()
            total_overlap = 0

            for user_slot in user_time_slots:
                for group_slot in group_time_slots:
                    if user_slot.day_of_week == group_slot.day_of_week:
                        overlap = min(user_slot.end_time, group_slot.end_time) - max(user_slot.start_time, group_slot.start_time)
                        if overlap > 0:
                            total_overlap += overlap
            
            if group.neighborhood == loc:
                total_overlap *= 1.3
            
            if user not in group.members.all():    
                group_matches.append((group, total_overlap))
            
            if len(group_matches) == 25:
                break
                
        group_matches.sort(key=lambda x: x[1], reverse=True)
        group_matches = [group[0] for group in group_matches]
        redis_client.set(f'user:{user.id}:matching_groups', ','.join([str(group.id) for group in group_matches]), ex=60)
        
        return group_matches
    

class AllGroupsService:
    @staticmethod
    def get_all_groups() -> QuerySet[Group]:
        return Group.objects.all()
