from rest_framework import serializers
from authentication.models import User
from groups.models import *

VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['title', 'description', 'level', 'city', 'neighborhood', 'meeting_url', 'private']

    

class GroupRetrieveSerializer(serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField(read_only=True)
    member_usernames = serializers.SerializerMethodField(read_only=True)
    number_of_members = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'image', 'level', 'city', 'neighborhood', 
                  'created_at', 'meeting_url', 'private', 
                  'owner_username', 'member_usernames', 'number_of_members']


    def get_owner_username(self, obj):
        return obj.owner.username if obj.owner else None

    def get_member_usernames(self, obj):
        return [member.username for member in obj.members.all()]
    
    def get_number_of_members(self, obj):
        return obj.members.count()


class GroupPendingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'profile_image', 'level']
        
    def get_pending_members(self, obj):
        return [member.username for member in obj.pending_members.all()]
    

class GroupAcceptRequestSerializer(serializers.Serializer):
    username = serializers.CharField()

class GroupDeclineRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
   
class GroupKickSerializer(serializers.Serializer):
    username = serializers.CharField()
    
class GroupMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'profile_image', 'level']