web: gunicorn app:server --workers 4
worker: celery -A app:celery_instance worker --loglevel=info


