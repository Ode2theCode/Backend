from django.db.models import QuerySet

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
        
    def get_group_time_slots(group) -> QuerySet[GroupTimeSlot]:
        return GroupTimeSlot.objects.filter(group=group)
    
    @staticmethod
    def delete_time_slot(user, time_slot_id: int) -> None:
        time_slot = GroupTimeSlot.objects.filter(
            id=time_slot_id,
            user=user
        ).first()
        
        if not time_slot:
            raise ValidationError({'detail': 'Time slot not found', 'status': status.HTTP_404_NOT_FOUND})
            
        time_slot.delete()
    
    
    
class HomeService:
    def get_joined_groups(user) -> list[Group]:
        return Group.objects.filter(members=user)
    
class SuggestionService:
    
    def get_suggestions(user) -> list[Group]:
        user_time_slots = UserTimeSlotService.get_user_time_slots(user)
        groups = Group.objects.exclude(members=user)
        group_matches = []
        
        for group in groups:
            group_time_slots = GroupTimeSlotService.get_group_time_slots(group)
            total_overlap = 0

            for user_slot in user_time_slots:
                for group_slot in group_time_slots:
                    if user_slot.day_of_week == group_slot.day_of_week:
                        overlap = min(user_slot.end_time, group_slot.end_time) - max(user_slot.start_time, group_slot.start_time)
                        if overlap > 0:
                            total_overlap += overlap

            if total_overlap > 0:
                group_matches.append((group, total_overlap))
                
        group_matches.sort(key=lambda x: x[1], reverse=True)
        
        return group_matches
    

class AllGroupsService:
    @staticmethod
    def get_all_groups(request) -> QuerySet[Group]:
        queryset = Group.objects.all()
        filterset = GroupFilter(request.GET, queryset=queryset)
        return filterset.qs