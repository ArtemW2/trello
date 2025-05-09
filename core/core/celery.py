import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace = 'CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_deadlines_': {
        'task': 'task.tasks.check_deadlines',
        'schedule': crontab(hour = 0, minute = 0)
    },
    'check_metrics': {
        'task': 'metrics.tasks.update_metrics_daily',
        'schedule': crontab(hour = 23, minute = 0)
    },
}
