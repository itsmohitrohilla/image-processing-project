#!/bin/bash

# Start FastAPI server
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.tasks worker --loglevel=info


