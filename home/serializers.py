from rest_framework import serializers

from .models import *
from authentication.models import User
from groups.models import Group

class HomeSerializer(serializers.Serializer):
    joined_groups = serializers.SerializerMethodField()
    pending_groups = serializers.SerializerMethodField()
    
    class meta:
        model = User
        fields = ['joined_groups', 'pending_groups']
        
    def get_joined_groups(self, obj):
        joined_groups = [group.title for group in obj.joined_groups.all()]
        return joined_groups
    
    def get_pending_groups(self, obj):
        pending_groups = [group.title for group in obj.pending_groups.all()]
        return pending_groups
    
    
class UserTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTimeSlot
        fields = ['id', 'day_of_week', 'start_time', 'end_time']
        read_only_fields = ['id']
        
class GroupTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupTimeSlot
        fields = ['id', 'day_of_week', 'start_time', 'end_time']
        
class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'level', 'city', 'neighborhood', 'created_at', 'max_members', 'meeting_url', 'private']
        

        