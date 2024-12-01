import django_filters
from groups.models import Group

class GroupFilter(django_filters.FilterSet):
    time_slots = django_filters.CharFilter(method='filter_time_slots')
    
    class Meta:
        model = Group
        fields = {
            'level': ['exact'],
            'neighborhood': ['exact'],
            'time_slots': ['exact']
        }
        
    def filter_time_slots(self, queryset, name, value):
        time_slots = value.split(',')
        for time_slot in time_slots:
            day, start, end = time_slot.split(':')
            queryset = queryset.filter(
                day_of_week=day,
                start_time=start,
                end_time=end
            )
        
        return queryset