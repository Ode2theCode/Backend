from rest_framework import serializers
from groups.models import *

VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        
    def validate(self, data):
        # For create operation
        if not self.instance:
            if Group.objects.filter(title=data.get('title')).exists():
                raise serializers.ValidationError('group title already exists')
                
        if 'level' in data and data['level'] not in VALID_LEVELS:
            raise serializers.ValidationError(
                f'Invalid level. Please select one of the following: {", ".join(VALID_LEVELS)}'
            )
        return data


















# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = '__all__'
        
#     def create(self, validated_data):
#         if Group.objects.filter(title=validated_data['title']).exists():
#             raise serializers.ValidationError('group title already exists')
        
#         if validated_data['level'] not in VALID_LEVELS:
#             raise serializers.ValidationError('Invalid level. please select one of the following: A1, A2, B1, B2, C1, C2')
        
#         group = Group.objects.create(**validated_data)
#         return group
        
# class GroupUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = ['level', 'city', 'neighborhood']
    
#     def update(self, instance, validated_data):
#         # if Group.objects.filter(title=validated_data['title']).exists():
#         #     raise serializers.ValidationError('group title already exists')
        
#         # if validated_data['level'] not in VALID_LEVELS:
#         #     raise serializers.ValidationError('Invalid level. please select one of the following: A1, A2, B1, B2, C1, C2')
        
#         instance.title = validated_data.get('title', instance.title)
#         instance.level = validated_data.get('level', instance.level)
#         instance.city = validated_data.get('city', instance.city)
#         instance.neighborhood = validated_data.get('neighborhood', instance.neighborhood)
#         instance.save()
        
#         return instance