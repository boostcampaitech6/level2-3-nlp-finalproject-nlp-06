#!/bin/bash

# Exit on error
set -e

# Wait for database to be ready
python manage.py wait_for_db

# Apply database migrations
python manage.py migrate

# Apply initidal db contiguration
python manage.py initialize_data

# Collect static files
python manage.py collectstatic --noinput

# Start the Django application
# For Uvicorn:
uvicorn core.asgi:application --host 0.0.0.0 --port 8000