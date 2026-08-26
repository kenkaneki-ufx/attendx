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
        # Note: Database uses KCS/KAS/KNC prefix codes
        assignments = [
            # (username, subject_code)
            ('anshika.yadav', 'KCS302'),    # Computer Organization
            ('anshika.yadav', 'KCS352'),    # CO Lab
            ('dileep.gupta', 'KCS303'),     # Discrete Structures
            ('sarita.maurya', 'KNC402'),    # Python Programming
            ('abhinav.verma', 'KAS302'),    # Maths IV
            ('anita.pal', 'KCS301'),        # Data Structure
            ('anita.pal', 'KCS351'),        # DS Lab
            ('manju.singh', 'KAS301'),      # Technical Communication
            ('pankaj.gupta', 'KCS353'),     # Web Design Workshop
            ('kamal.tiwari', 'KCS354'),     # Internship Assessment
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
