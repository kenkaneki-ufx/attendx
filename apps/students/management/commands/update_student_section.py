"""
Management command to update students from CS31 to CS21.
Run: python manage.py update_student_section
"""
from django.core.management.base import BaseCommand
from apps.students.models import Student
from apps.sections.models import Section


class Command(BaseCommand):
    help = 'Update students from CS31 to CS21'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Updating student sections...\n'))

        # Get sections
        try:
            old_section = Section.objects.get(name='CS31')
            self.stdout.write(f'  Found old section: {old_section}')
        except Section.DoesNotExist:
            self.stdout.write(self.style.WARNING('  Section CS31 not found'))
            old_section = None

        try:
            new_section = Section.objects.get(name='CS21')
            self.stdout.write(f'  Found new section: {new_section}')
        except Section.DoesNotExist:
            self.stdout.write(self.style.ERROR('  Section CS21 not found!'))
            return

        if old_section:
            # Update all students from CS31 to CS21
            students = Student.objects.filter(section=old_section)
            count = students.count()
            self.stdout.write(f'\n  Found {count} students in CS31')
            
            students.update(section=new_section)
            self.stdout.write(self.style.SUCCESS(f'  Updated {count} students to CS21'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('SECTION UPDATE COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Students in CS21: {Student.objects.filter(section=new_section).count()}')
        self.stdout.write(self.style.SUCCESS('='*60))
