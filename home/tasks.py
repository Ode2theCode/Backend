from django.db.models import F, ExpressionWrapper, FloatField, Case, When
from celery import shared_task
from django.contrib.auth import get_user_model
import redis
from dotenv import load_dotenv
import os

from groups.models import Group
from home.services import UserTimeSlotService, GroupTimeSlotService
from home.models import GroupTimeSlot

from django.db.models import Case, When, Value, FloatField, F, ExpressionWrapper, Sum
from django.db.models.functions import Coalesce

from home.models import UserSuggestions

load_dotenv()


@shared_task
def find_matching_groups(user):
    VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    user_level = user.level.upper()
    level_index = VALID_LEVELS.index(user_level)
    levels_to_consider = [user_level]
    if level_index > 0:
        levels_to_consider.append(VALID_LEVELS[level_index - 1])
    if level_index < len(VALID_LEVELS) - 1:
        levels_to_consider.append(VALID_LEVELS[level_index + 1])
    
    user_time_slots = UserTimeSlotService.get_user_time_slots(user)
    
    groups = Group.objects.filter(level__in=levels_to_consider)\
        .exclude(id__in=[group.id for group in user.groups.all()])\
        .order_by('?')[:1000].annotate(
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
            output_field=FloatField()
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
    return best_fit_groups

@shared_task
def cache_matching_groups():
    User = get_user_model()
    users = User.objects.all()
    
    for user in users:
        matching_groups = find_matching_groups(user)
        matching_group_ids = [group.id for group in matching_groups]
        UserSuggestions.objects.update_or_create(user_id=user.id, defaults={'group_ids': ','.join(map(str, matching_group_ids))})
