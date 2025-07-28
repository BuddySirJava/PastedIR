#!/bin/bash

# Start Celery worker
echo "Starting Celery worker..."
celery -A pastebinir worker --loglevel=info --concurrency=2 &

# Start Celery beat
echo "Starting Celery beat..."
celery -A pastebinir beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

# Wait for background processes
wait 