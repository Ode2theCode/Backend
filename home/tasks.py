from django.db.models import F, ExpressionWrapper, FloatField, Case, When
from celery import shared_task
from django.contrib.auth import get_user_model
import redis
from dotenv import load_dotenv
import os

from groups.models import Group
from home.services import UserTimeSlotService, GroupTimeSlotService
from home.models import GroupTimeSlot

load_dotenv()

redis_url = os.getenv('REDIS_URL')
redis_client = redis.StrictRedis.from_url(redis_url)

@shared_task
def find_matching_groups(user):
    loc = None
    if user.neighborhood:
        loc = user.neighborhood
    user_time_slots = UserTimeSlotService.get_user_time_slots(user)
    groups = Group.objects.all()
    group_matches = []
    for group in groups:
        group_time_slots = GroupTimeSlotService.get_group_time_slots(group.title)
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
    group_ids = [group[0].id for group in group_matches]    
    return group_ids

@shared_task
def cache_matching_groups():
    User = get_user_model()
    users = User.objects.all()
    
    for user in users:
        matching_groups = find_matching_groups(user)
        redis_client.set(f'user:{user.id}:matching_groups', matching_groups)