#!/usr/bin/env bash
# exit on error
set -o errexit

# Set Django settings for build
export DJANGO_SETTINGS_MODULE=config.settings.production

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (first deploy only)
python manage.py shell -c "
from apps.accounts.models import Faculty
if not Faculty.objects.filter(username='admin').exists():
    Faculty.objects.create_superuser(
        username='admin',
        email='admin@attendx.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        employee_id='ADMIN001'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
