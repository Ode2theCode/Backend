import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FD.settings')

app = Celery('FD')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cache-matching-groups': {
        'task': 'home.tasks.cache_matching_groups',
        'schedule': crontab(hour=2),
    },
    'test-celery': {
        'task': 'home.tasks.test_celery',
        'schedule': crontab(minute=1),
    },
}