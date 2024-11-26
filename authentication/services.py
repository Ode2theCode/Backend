from rest_framework.exceptions import ValidationError
from rest_framework import status

from .models import *

class UserService:
    VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    
    @classmethod
    def check_level(cls, level):
        if level not in cls.VALID_LEVELS:
            raise ValidationError({'detail': f'Invalid level. Please select one of the following: {", ".join(cls.VALID_LEVELS)}', 'status': status.HTTP_400_BAD_REQUEST})
    
    @classmethod
    def update_user(cls, user, data):
        user.level = data.get('level', user.level)
        cls.check_level(user.level)
        user.city = data.get('city', user.city)
        user.neighborhood = data.get('neighborhood', user.neighborhood)
        user.profile_image = data.get('profile_image', user.profile_image)
        user.save()
        return user
        
    
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError({'detail': 'Invalid password', 'status': status.HTTP_400_BAD_REQUEST})
        
        if old_password == new_password:
            raise ValidationError({'detail': 'New password cannot be the same as the old password', 'status': status.HTTP_400_BAD_REQUEST})
        
        user.set_password(new_password)
        user.save()
        return user