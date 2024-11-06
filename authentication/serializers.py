from rest_framework import serializers

from FD import settings
from .models import *

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        otp = attrs.get('otp')
        
        try:
            otp_obj = OneTimePassword.objects.get(otp=otp)
            user = otp_obj.user
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return user
            
            else:
                raise serializers.ValidationError('account already verified')
            
        except OneTimePassword.DoesNotExist:
            raise serializers.ValidationError('invalid one time password')
    