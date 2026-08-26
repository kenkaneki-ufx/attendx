"""
Management command to seed faculty accounts from CS21 timetable.
Run: python manage.py seedfaculty
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import Faculty
from apps.departments.models import Department


class Command(BaseCommand):
    help = 'Seed faculty accounts from CS21 timetable'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting faculty seeding...\n'))

        # Get CSE department
        try:
            cse_dept = Department.objects.get(code='CSE')
            self.stdout.write(f'  Found department: {cse_dept}')
        except Department.DoesNotExist:
            self.stdout.write(self.style.ERROR('  CSE Department not found! Run seedaktu first.'))
            return

        # Faculty data from CS21 timetable
        faculty_data = [
            {
                'username': 'anshika.yadav',
                'email': 'anshika.yadav@goelco.edu.in',
                'first_name': 'Anshika',
                'last_name': 'Yadav',
                'employee_id': 'FAC001',
                'phone': '9876543201',
                'subjects': 'BCS302 - Computer Organization and Architecture, BCS352 - Computer Organization Lab',
            },
            {
                'username': 'dileep.gupta',
                'email': 'dileep.gupta@goelco.edu.in',
                'first_name': 'Dileep',
                'last_name': 'Kumar Gupta',
                'employee_id': 'FAC002',
                'phone': '9876543202',
                'subjects': 'BCS303 - Discrete Structures & Theory of Logic',
            },
            {
                'username': 'sarita.maurya',
                'email': 'sarita.maurya@goelco.edu.in',
                'first_name': 'Sarita',
                'last_name': 'Maurya',
                'employee_id': 'FAC003',
                'phone': '9876543203',
                'subjects': 'BCC302 - Python Programming',
            },
            {
                'username': 'abhinav.verma',
                'email': 'abhinav.verma@goelco.edu.in',
                'first_name': 'Abhinav',
                'last_name': 'Verma',
                'employee_id': 'FAC004',
                'phone': '9876543204',
                'subjects': 'BAS303 - Maths IV',
            },
            {
                'username': 'anita.pal',
                'email': 'anita.pal@goelco.edu.in',
                'first_name': 'Anita',
                'last_name': 'Pal',
                'employee_id': 'FAC005',
                'phone': '9876543205',
                'subjects': 'BCS301 - Data Structure, BCS351 - Data Structures Using C Lab',
            },
            {
                'username': 'manju.singh',
                'email': 'manju.singh@goelco.edu.in',
                'first_name': 'Manju',
                'last_name': 'Singh',
                'employee_id': 'FAC006',
                'phone': '9876543206',
                'subjects': 'BAS301 - Technical Communication',
            },
            {
                'username': 'pankaj.gupta',
                'email': 'pankaj.gupta@goelco.edu.in',
                'first_name': 'Pankaj',
                'last_name': 'Kumar Gupta',
                'employee_id': 'FAC007',
                'phone': '9876543207',
                'subjects': 'BCS353 - Web Design Workshop Lab',
            },
            {
                'username': 'kamal.tiwari',
                'email': 'kamal.tiwari@goelco.edu.in',
                'first_name': 'Kamal',
                'last_name': 'Nayan Tiwari',
                'employee_id': 'FAC008',
                'phone': '9876543208',
                'subjects': 'BCC351 - Internship Assessment / Mini Project',
            },
        ]

        created_count = 0
        for data in faculty_data:
            faculty, created = Faculty.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'employee_id': data['employee_id'],
                    'phone': data['phone'],
                    'department': cse_dept,
                }
            )
            
            if created:
                # Set a default password
                faculty.set_password('faculty123')
                faculty.save()
                created_count += 1
                self.stdout.write(f'  Created: {faculty.get_full_name()} ({faculty.employee_id})')
            else:
                self.stdout.write(f'  Exists: {faculty.get_full_name()} ({faculty.employee_id})')

        # ========== SUMMARY ==========
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('FACULTY SEEDING COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Total Faculty: {Faculty.objects.count()}')
        self.stdout.write(f'  New created: {created_count}')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\nDefault password for all faculty: faculty123')
        self.stdout.write('\nFaculty subjects assigned:')
        for data in faculty_data:
            self.stdout.write(f'  {data["first_name"]} {data["last_name"]}: {data["subjects"]}')
