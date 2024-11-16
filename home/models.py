from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class TimeSlot(models.Model):
    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='time_slots')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    def __str__(self):
        return f"{self.day_of_week} {self.start_time} - {self.end_time}"