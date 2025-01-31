# valentine_project/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valentine_project.settings')

# Create the Celery application
app = Celery('valentine_project')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat schedule
app.conf.beat_schedule = {
    'check-scheduled-messages': {
        'task': 'messages_app.tasks.send_scheduled_messages',
        'schedule': crontab(minute='*/1'),
    },
}

# Additional Celery settings
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
)

# Auto-discover tasks
app.autodiscover_tasks()