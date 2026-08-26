"""
Management command to create CS21 section and move students from CS31.
Run: python manage.py fix_cs21
"""
from django.core.management.base import BaseCommand
from apps.students.models import Student
from apps.sections.models import Section
from apps.branches.models import Branch


class Command(BaseCommand):
    help = 'Create CS21 section and move students from CS31'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Fixing CS21 section...\n'))

        # Get CSE branch
        try:
            cse_branch = Branch.objects.get(code='CSE')
            self.stdout.write(f'  Found branch: {cse_branch}')
        except Branch.DoesNotExist:
            self.stdout.write(self.style.ERROR('  CSE Branch not found!'))
            return

        # Create CS21 section if it doesn't exist
        cs21, created = Section.objects.get_or_create(
            name='CS21',
            branch=cse_branch,
            semester=3,
            defaults={'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  Created section: {cs21}'))
        else:
            self.stdout.write(f'  Section already exists: {cs21}')

        # Get old section CS31
        try:
            old_section = Section.objects.get(name='CS31')
            self.stdout.write(f'  Found old section: {old_section}')
            
            # Update students from CS31 to CS21
            students = Student.objects.filter(section=old_section)
            count = students.count()
            self.stdout.write(f'\n  Found {count} students in CS31')
            
            students.update(section=cs21)
            self.stdout.write(self.style.SUCCESS(f'  Updated {count} students to CS21'))
            
        except Section.DoesNotExist:
            self.stdout.write(self.style.WARNING('  Section CS31 not found - no students to move'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('CS21 FIX COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Students in CS21: {Student.objects.filter(section=cs21).count()}')
        self.stdout.write(self.style.SUCCESS('='*60))
