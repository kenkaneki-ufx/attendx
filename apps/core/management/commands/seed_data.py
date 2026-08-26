"""
Seed the database with a superuser for AttendX.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

Faculty = get_user_model()


class Command(BaseCommand):
    help = 'Create the admin superuser'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating superuser...'))

        if not Faculty.objects.filter(username='admin').exists():
            Faculty.objects.create_superuser(
                username='admin',
                email='admin@attendx.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                employee_id='ADM001',
            )
            self.stdout.write(self.style.SUCCESS('Superuser created: admin / admin123'))
        else:
            self.stdout.write('Superuser "admin" already exists.')

        self.stdout.write(self.style.SUCCESS('Done!'))
