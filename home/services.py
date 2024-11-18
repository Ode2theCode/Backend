from django.db.models import QuerySet

from rest_framework.exceptions import ValidationError

from .models import *
from groups.models import *

class TimeSlotService:
    @staticmethod
    def validate_time_range(start_time: float, end_time: float) -> None:
        if not (0 <= start_time <= 24 and 0 <= end_time <= 24):
            raise ValidationError('Time must be between 0 and 24')
            
        if end_time <= start_time:
            raise ValidationError('End time must be after start time')

    @staticmethod
    def validate_overlap(user, day_of_week: str, start_time: float, end_time: float) -> None:
        
        overlapping = TimeSlot.objects.filter(
            user=user,
            day_of_week=day_of_week.lower(),
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        if overlapping.exists():
            raise ValidationError('This time slot overlaps with an existing slot')

    @classmethod
    def create_time_slot(cls, user, day_of_week: str, start_time: float, end_time: float) -> TimeSlot:
        
        cls.validate_time_range(start_time, end_time)
        cls.validate_overlap(user, day_of_week, start_time, end_time)
        
        time_slot = TimeSlot.objects.create(
            user=user,
            day_of_week=day_of_week.lower(),
            start_time=start_time,
            end_time=end_time
        )

        return time_slot
    
    @classmethod
    def create_group_time_slot(cls, group, day_of_week: str, start_time: float, end_time: float) -> TimeSlot:
        
        cls.validate_time_range(start_time, end_time)
        cls.validate_overlap(group, day_of_week, start_time, end_time)
        
        time_slot = GroupTimeSlot.objects.create(
            group=group,
            day_of_week=day_of_week.lower(),
            start_time=start_time,
            end_time=end_time
        )

        return time_slot
    
    def get_user_time_slots(user) -> QuerySet[TimeSlot]:
        return TimeSlot.objects.filter(user=user)
    
    def get_group_time_slots(group) -> QuerySet[TimeSlot]:
        return GroupTimeSlot.objects.filter(group=group)

    @staticmethod
    def delete_time_slot(user, time_slot_id: int) -> None:
        time_slot = TimeSlot.objects.filter(
            id=time_slot_id,
            user=user
        ).first()
        
        if not time_slot:
            raise ValidationError('Time slot not found')
            
        time_slot.delete()
        
class SuggestionService:
    
    def get_suggestions(user) -> list[Group]:
        user_time_slots = TimeSlotService.get_user_time_slots(user)
        groups = Group.objects.exclude(members=user)
        group_matches = []
        
        for group in groups:
            group_time_slots = TimeSlotService.get_group_time_slots(group)
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
        
        
                