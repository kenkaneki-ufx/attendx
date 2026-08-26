from django.core.management.base import BaseCommand
from apps.accounts.models import Faculty
from apps.subjects.models import Subject
from apps.sections.models import Section
from apps.faculty.models import FacultySubjectAssignment


class Command(BaseCommand):
    help = 'Seed faculty subject assignments for CS21 section'

    def handle(self, *args, **options):
        self.stdout.write('Seeding faculty subject assignments...\n')
        
        # Get the CS21 section (Semester 3)
        try:
            section = Section.objects.get(name='CS21', semester=3)
            self.stdout.write(f'Found section: {section.name}')
        except Section.DoesNotExist:
            self.stdout.write(self.style.ERROR('Section CS21 not found!'))
            return
        
        # Academic year
        academic_year = '2025-2026'
        
        # Faculty to subject assignments based on timetable
        assignments = [
            # (username, subject_code)
            ('anshika.yadav', 'BCS302'),    # Computer Organization
            ('anshika.yadav', 'BCS352'),    # CO Lab
            ('dileep.gupta', 'BCS303'),     # Discrete Structures
            ('sarita.maurya', 'BCC302'),    # Python Programming
            ('abhinav.verma', 'BAS303'),    # Maths IV
            ('anita.pal', 'BCS301'),        # Data Structure
            ('anita.pal', 'BCS351'),        # DS Lab
            ('manju.singh', 'BAS301'),      # Technical Communication
            ('pankaj.gupta', 'BCS353'),     # Web Design Workshop
            ('kamal.tiwari', 'BCC351'),     # Internship Assessment
        ]
        
        created_count = 0
        skipped_count = 0
        
        for username, subject_code in assignments:
            try:
                faculty = Faculty.objects.get(username=username)
                subject = Subject.objects.get(code=subject_code)
                
                assignment, created = FacultySubjectAssignment.objects.get_or_create(
                    faculty=faculty,
                    subject=subject,
                    section=section,
                    academic_year=academic_year,
                    defaults={'is_active': True}
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✅ Created: {faculty.get_full_name()} -> {subject.code} ({section.name})')
                else:
                    skipped_count += 1
                    self.stdout.write(f'  ⏭️  Skipped (exists): {faculty.get_full_name()} -> {subject.code}')
                    
            except Faculty.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Faculty not found: {username}'))
            except Subject.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Subject not found: {subject_code}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done! Created: {created_count}, Skipped: {skipped_count}'
        ))
