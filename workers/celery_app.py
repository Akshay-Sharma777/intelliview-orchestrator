"""Celery Application Setup.
Initialises Celery with the Redis broker, sensible reliability defaults,
and a `session_failed` signal that lets us mark the DB session as
FAILED only after Celery has exhausted its retries.
"""

from celery import Celery, signals
from kombu import Queue
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from config import REDIS_URL
from metrics.prometheus_metrics import TASKS_PERMANENTLY_FAILED

celery_app = Celery("interview_tasks", broker=REDIS_URL, backend=REDIS_URL)
EVALUATION_MAX_RETRIES = 3
EVALUATION_RETRY_BACKOFF_BASE = 2
EVALUATION_RETRY_BACKOFF_MAX = 60
CeleryInstrumentor().instrument()


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    task_acks_late=True,  # re-deliver if worker dies mid-task
    task_reject_on_worker_lost=True,
    # Long-running interview tasks should reserve only one task at a time
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    # All interview tasks dispatch to the "fast" queue by default (the worker
    # consumes only "fast"/"slow"); without this the tasks land on the default
    # "celery" queue, which no worker reads, and sessions stay QUEUED forever.
    task_default_queue="fast",
    task_queues=(
        Queue("fast"),
        Queue("slow"),
    ),
    task_routes={
        "workers.tasks.scan_and_dispatch_retries": {"queue": "fast"},
    },
    beat_schedule={
        "scan-due-retries": {
            "task": "workers.tasks.scan_and_dispatch_retries",
            "schedule": 60.0,
        },
        "detect-no-shows": {
            "task": "workers.tasks.detect_no_shows",
            "schedule": 60.0,
        },
    },
)

# Auto-discover tasks from workers module
celery_app.autodiscover_tasks(["workers"])

_SESSION_TASK_NAMES: frozenset[str] = frozenset(
    {
        "workers.tasks.process_interview_session",
        "workers.tasks._run_video",
        "workers.tasks._run_audio",
        "workers.tasks._after_parallel",
    }
)
"""Tasks that carry a