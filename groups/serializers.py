from rest_framework import serializers
from groups.models import *

VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['title', 'description', 'level', 'city', 'neighborhood', 'max_members', 'meeting_url', 'private']
        
    def validate(self, data):
        if Group.objects.filter(title=data.get('title')).exists():
            raise serializers.ValidationError('group title already exists')
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        Group.objects.create(
            title=validated_data.get('title'),
            description=validated_data.get('description'),
            level=validated_data.get('level'),
            city=validated_data.get('city'),
            neighborhood=validated_data.get('neighborhood'),
            max_members=validated_data.get('max_members'),
            meeting_url=validated_data.get('meeting_url'),
            private=validated_data.get('private'),
            owner=user
        )
        group = Group.objects.get(title=validated_data.get('title'))
        group.add_member(user)
        # user.joined_groups.add(group)
        return group
    

class GroupRetrieveSerializer(serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField(read_only=True)
    member_usernames = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'level', 'city', 'neighborhood', 
                  'created_at', 'max_members', 'meeting_url', 'private', 
                  'owner_username', 'member_usernames']

    def get_owner_username(self, obj):
        return obj.owner.username if obj.owner else None

    def get_member_usernames(self, obj):
        return [member.username for member in obj.members.all()]


class GroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['title', 'description', 'level', 'city', 'neighborhood', 'max_members', 'meeting_url', 'private']
        
    def validate(self, data):
        if 'level' in data and data['level'] not in VALID_LEVELS:
            raise serializers.ValidationError(
                f'Invalid level. Please select one of the following: {", ".join(VALID_LEVELS)}'
            )
    
        if 'title' in data and Group.objects.filter(title=data['title']).exists():
            raise serializers.ValidationError('group title already exists')
        
        return data
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.level = validated_data.get('level', instance.level)
        instance.city = validated_data.get('city', instance.city)
        instance.neighborhood = validated_data.get('neighborhood', instance.neighborhood)
        instance.max_members = validated_data.get('max_members', instance.max_members)
        instance.meeting_url = validated_data.get('meeting_url', instance.meeting_url)
        instance.private = validated_data.get('private', instance.private)
        instance.save()
        return instance