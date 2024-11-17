from rest_framework import serializers
from authentication.models import User
from .models import *

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
    
class TimeSlotCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['day_of_week', 'start_time', 'end_time']

    def validate(self, data):
        user = self.context.get('user')
        if TimeSlot.objects.filter(
            day_of_week=data.get('day_of_week'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            user=user
        ).exists():
            raise serializers.ValidationError('time slot already exists')
        
        if data['end_time'] < data['start_time']:
            raise serializers.ValidationError('end time must be greater than start time')
        
        return data

class TimeSlotListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['day_of_week', 'start_time', 'end_time']
        
        
class TimeSlotDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['day_of_week', 'start_time', 'end_time']
        
    def validate(self, data):
        if TimeSlot.objects.filter(
            day_of_week=data.get('day_of_week'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            user=self.context.get('user')
        ).exists():
            return data
        else:
            raise serializers.ValidationError('time slot does not exist')
    
    def delete(self):
        user = self.context.get('user')
        TimeSlot.objects.filter(
            day_of_week=self.validated_data.get('day_of_week'),
            start_time=self.validated_data.get('start_time'),
            end_time=self.validated_data.get('end_time'),
            user=user
        ).delete()
    