import redis
from dotenv import load_dotenv
import os
from groups.models import Group

from django.db.models import Case, When, Value, FloatField, F, ExpressionWrapper, Sum
from django.db.models.functions import Coalesce
import random

load_dotenv()


from django.db.models import QuerySet

from rest_framework.exceptions import ValidationError
from rest_framework import status


from .models import *
from groups.models import *



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
            start_time__lte=end_time,
            end_time__gte=start_time
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
            start_time__lte=end_time,
            end_time__gte=start_time
        )
        
        if overlapping.exists():
            raise ValidationError({'detail': 'This time slot overlaps with an existing slot', 'status': status.HTTP_400_BAD_REQUEST})


    @classmethod
    def create_group_time_slot(cls, title, user, day_of_week: str, start_time: float, end_time: float) -> GroupTimeSlot:
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if Group.objects.get(title=title).owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        group = Group.objects.get(title=title)
        print(group.owner)
        print(user)
        cls.validate_time_range(start_time, end_time)
        cls.validate_overlap(group, day_of_week, start_time, end_time)
        
        time_slot = GroupTimeSlot.objects.create(
            group=group,
            day_of_week=day_of_week.lower(),
            start_time=start_time,
            end_time=end_time
        )

        return time_slot
        
    def get_group_time_slots(title, user) -> QuerySet[GroupTimeSlot]:
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if not Group.objects.get(title=title).members.filter(username=user.username).exists():
            raise ValidationError({'detail': 'You are not a member of this group', 'status': status.HTTP_403_FORBIDDEN})
        
        group = Group.objects.get(title=title)
        return group.time_slots.all()
    
    @staticmethod
    def delete_time_slot(title, time_slot_id: int, user) -> None:
        if not Group.objects.filter(title=title).exists():
            raise ValidationError({'detail': 'Group not found', 'status': status.HTTP_404_NOT_FOUND})
        
        if Group.objects.get(title=title).owner != user:
            raise ValidationError({'detail': 'You are not the owner of this group', 'status': status.HTTP_403_FORBIDDEN})
        
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
        
        if UserSuggestions.objects.filter(user_id=user.id).exists():
            group_ids = UserSuggestions.objects.get(user_id=user.id).group_ids
            group_ids = group_ids.split(',')
            group_ids = [int(group_id) for group_id in group_ids]
            groups = Group.objects.filter(id__in=group_ids)
            return groups
        
        VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        user_level = user.level.upper()
        level_index = VALID_LEVELS.index(user_level)
        levels_to_consider = [user_level]
        if level_index > 0:
            levels_to_consider.append(VALID_LEVELS[level_index - 1])
        if level_index < len(VALID_LEVELS) - 1:
            levels_to_consider.append(VALID_LEVELS[level_index + 1])
        
        user_time_slots = UserTimeSlotService.get_user_time_slots(user)
        user_group_ids = list(user.joined_groups.values_list('id', flat=True))
        
        
        groups = Group.objects.filter(level__in=levels_to_consider)\
            .exclude(id__in=user_group_ids)\
            .annotate(
                total_overlap=Coalesce(
                    Sum(
                        ExpressionWrapper(
                            Case(
                                *[
                                    When(
                                        time_slots__day_of_week=user_slot.day_of_week,
                                        then=F('time_slots__end_time') - F('time_slots__start_time')
                                    )
                                    for user_slot in user_time_slots
                                ],
                                output_field=FloatField()
                            ),
                            output_field=FloatField()
                        )
                    ),
                    Value(0.0),
                )
            )
        
        if user.neighborhood:
            groups = groups.annotate(
                total_overlap=ExpressionWrapper(
                    F('total_overlap') * Case(
                        When(neighborhood=user.neighborhood, then=1.3),
                        default=1,
                        output_field=FloatField()
                    ),
                    output_field=FloatField()
                )
            )
        
        best_fit_groups = groups.order_by('-total_overlap')[:25]
        UserSuggestions.objects.create(user_id=user.id, group_ids=','.join([str(group.id) for group in best_fit_groups]))
        return best_fit_groups

class AllGroupsService:
    @staticmethod
    def get_all_groups(user) -> QuerySet[Group]:
        return Group.objects.exclude(members=user)

