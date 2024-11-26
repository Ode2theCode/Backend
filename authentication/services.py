from rest_framework.exceptions import ValidationError
from rest_framework import status

class UserService:
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError({'detail': 'Invalid password', 'status': status.HTTP_400_BAD_REQUEST})
        
        if old_password == new_password:
            raise ValidationError({'detail': 'New password cannot be the same as the old password', 'status': status.HTTP_400_BAD_REQUEST})
        
        user.set_password(new_password)
        user.save()
        return user