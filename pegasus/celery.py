import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pegasus.settings")

app = Celery("hospital")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


app.conf.beat_schedule = {
    "generate-slots-daily": {
        "task":     "apps.slots.tasks.generate_slots_for_all_doctors_task",
        "schedule": crontab(hour=0, minute=0),
        "kwargs":   {"days_ahead": 14},
    },
}

app.conf.timezone = "UTC"
