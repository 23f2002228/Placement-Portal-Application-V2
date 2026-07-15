from celery import Celery, Task
from celery.schedules import crontab

import config
from app import app


celery_app = Celery(
    "placement_portal_tasks",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["tasks"],
)


class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery_app.Task = FlaskTask
celery_app.conf.timezone = "Asia/Kolkata"

celery_app.conf.beat_schedule = {
    "daily-interview-reminders": {
        "task": "tasks.send_interview_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "monthly-company-placement-reports": {
        "task": "tasks.generate_monthly_company_reports",
        "schedule": crontab(hour=9, minute=0, day_of_month=1),
    },
}
