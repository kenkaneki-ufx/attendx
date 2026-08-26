#!/bin/bash

echo "Starting AttendX deployment..."

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('SUPERUSER_USERNAME', 'admin')
email = os.environ.get('SUPERUSER_EMAIL', 'admin@attendx.com')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    try:
        # Try Faculty model first (AttendX custom user)
        from apps.accounts.models import Faculty
        Faculty.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='User',
            employee_id='ADMIN001'
        )
        print(f'Superuser {username} created successfully!')
    except Exception as e:
        # Fallback to default User model
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f'Superuser {username} created (default model)!')
        except Exception as e2:
            print(f'Note: {e2}')
else:
    print(f'Superuser {username} already exists.')
"

# Seed AKTU data if database is empty
echo "Checking for AKTU data..."
python manage.py seedaktu

# Seed faculty accounts
echo "Seeding faculty accounts..."
python manage.py seedfaculty

# Seed CS21 timetable if empty
echo "Checking for CS21 timetable..."
python manage.py shell -c "from apps.lectures.models_timetable import Timetable; print(f'Timetable entries: {Timetable.objects.count()}') if Timetable.objects.exists() else __import__('django.core.management', fromlist=['call_command']).call_command('seedcs21timetable')"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
