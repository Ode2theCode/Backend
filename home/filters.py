import django_filters
from groups.models import Group

class GroupFilter(django_filters.FilterSet):
    class Meta:
        model = Group
        fields = {
            'level': ['exact'],
            'neighborhood': ['exact'],
            
                }