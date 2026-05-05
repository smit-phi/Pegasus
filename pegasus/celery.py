import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pegasus.settings")

app = Celery("hospital")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


app.conf.beat_schedule = {
    "generate-slots-daily": {
        "task":     "slots.tasks.generate_slots_for_all_doctor_task",
        "schedule": crontab(hour=0, minute=0),
        "kwargs":   {"days_ahead": 14},
    },
    "auto-update-past-appointments": {
        "task":     "appointments.tasks.auto_update_past_appointments",
        "schedule": crontab(hour=0, minute=15),
    },
}

app.conf.timezone = "UTC"
