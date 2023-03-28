#!/bin/bash

yes | python manage.py makemigrations &&
echo "yes" | python manage.py migrate &&
gunicorn --bind 0.0.0.0:8000 --workers 8 --access-logfile - --error-logfile - --log-level debug --timeout 90 todo.wsgi:application
