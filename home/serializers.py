from rest_framework import serializers

from .models import *
from authentication.models import User
from groups.models import Group

class HomeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Group
        fields = '__all__'
        
    
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
    requested = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'level', 'city', 'neighborhood', 'created_at', 'meeting_url', 'private', 'requested']
        
    def get_requested(self, obj):
        request = self.context['request']
        return request.user in obj.pending_members.all()
            
class GroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    requested = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'level', 'city', 'neighborhood', 'created_at', 'meeting_url', 'private', 'member_count', 'requestd']

        
    def get_member_count(self, obj):
        return obj.members.count()

    
class AllGroupsSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    requested = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'level', 'city', 'neighborhood', 'created_at', 'meeting_url', 'private', 'member_count', 'requested']
        
    def get_member_count(self, obj):
        return obj.members.count()

    def get_requested(self, obj):
        request = self.context['request']
        return request.user in obj.pending_members.all()

        