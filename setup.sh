#!/bin/bash

# Exit on error
set -e

# Define environment variables
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Check if virtual environment exists, if not, create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# Start FastAPI server
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.tasks worker --loglevel=info
