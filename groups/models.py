from django.db import models

class Group(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    max_members = models.IntegerField()
    meeting_url = models.URLField(blank=True, null=True)
    
    
    
    def __str__(self):
        return self.title