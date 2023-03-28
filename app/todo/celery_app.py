import os

from celery import Celery
from celery.schedules import crontab
from todo.settings_components.celery_config import CELERY_BROKER_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo.settings')

app = Celery('todo')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = CELERY_BROKER_URL


app.autodiscover_tasks()


app.conf.beat_schedule = {
    'delete-old-diaries': {
        'task': 'diary.tasks.task_delete_expired_diaries',
        'schedule': crontab(minute='*/10')
    }
}
