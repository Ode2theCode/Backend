from django.db.models import QuerySet

from rest_framework.exceptions import ValidationError

from .models import *

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