from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class UserTimeSlot(models.Model):
    day_of_week = models.CharField(max_length=255)
    start_time = models.FloatField()
    end_time = models.FloatField()
    
    user = models.ForeignKey('authentication.User', models.CASCADE, related_name='time_slots')
    
    def __str__(self):
        return f"{self.day_of_week} {self.start_time} - {self.end_time}"
    
class GroupTimeSlot(models.Model):
    day_of_week = models.CharField(max_length=255)
    start_time = models.FloatField()
    end_time = models.FloatField()
    
    group = models.ForeignKey('groups.Group', models.CASCADE, related_name='time_slots')
    
    def __str__(self):
        return f"{self.day_of_week} {self.start_time} - {self.end_time}"
    
class UserSuggestions(models.Model):
    user_id = models.IntegerField()
    group_ids = models.TextField()