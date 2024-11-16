from rest_framework import serializers
from authentication.models import User

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
    