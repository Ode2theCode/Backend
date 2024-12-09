from django.db import models

class Group(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='group_images/', null=True, blank=True)
    level = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meeting_url = models.URLField(blank=True, null=True)
    private = models.BooleanField(default=False)
    owner = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='owned_groups')
    members = models.ManyToManyField('authentication.User', related_name='joined_groups')
    pending_members = models.ManyToManyField('authentication.User', related_name='pending_groups')
    
    
    def add_pending_member(self, user):
        self.pending_members.add(user)
    

    def accept_pending_member(self, user):
        self.members.add(user)
        self.pending_members.remove(user)
    
    def decline_pending_member(self, user):
        self.pending_members.remove(user)
    
    def add_member(self, user):
        self.members.add(user)
        
    def remove_member(self, user):
        self.members.remove(user)
        
    def owner_username(self):
        return self.owner.username
    
    def members_usernames(self):
        return [member.username for member in self.members.all()]
    
    
    
    def __str__(self):
        return self.title