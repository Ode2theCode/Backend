from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def validate_email(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valid email address"))

    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError(_("The Username must be set"))
        if not email:
            raise ValueError(_("The Email must be set"))
        if not password:
            raise ValueError(_("The Password must be set"))
        
        email = self.normalize_email(email)
        self.validate_email(email)
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        
        user = self.create_user(username, email, password, **extra_fields)
        user.save(using= self._db)
        return user