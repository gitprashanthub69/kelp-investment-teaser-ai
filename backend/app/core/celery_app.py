import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
use_local = os.getenv("USE_LOCAL_STORAGE", "False").lower() == "true"

if use_local:
    # Use in-memory broker for local execution without Redis
    celery_app = Celery("worker", broker="memory://", backend="cache+memory://")
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    print("Celery running in local memory mode (no Redis)")
else:
    celery_app = Celery(
        "worker",
        broker=redis_url,
        backend=redis_url
    )

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Optional: automatically discover tasks in certain modules
celery_app.autodiscover_tasks(["app"])
