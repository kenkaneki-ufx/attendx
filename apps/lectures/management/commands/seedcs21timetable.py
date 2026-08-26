"""
Management command to seed CS21 timetable data.
Run: python manage.py seedcs21timetable
"""
from django.core.management.base import BaseCommand
from apps.lectures.models_timetable import TimeSlot, Timetable
from apps.subjects.models import Subject
from apps.sections.models import Section


class Command(BaseCommand):
    help = 'Seed CS21 timetable from AKTU schedule'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting CS21 timetable seeding...\n'))

        # ========== TIME SLOTS ==========
        time_slots_data = [
            {'slot_number': 1, 'start_time': '09:10', 'end_time': '10:10', 'label': '09:10 AM - 10:10 AM'},
            {'slot_number': 2, 'start_time': '10:10', 'end_time': '11:10', 'label': '10:10 AM - 11:10 AM'},
            {'slot_number': 3, 'start_time': '11:10', 'end_time': '12:10', 'label': '11:10 AM - 12:10 PM'},
            {'slot_number': 4, 'start_time': '12:10', 'end_time': '13:10', 'label': '12:10 PM - 01:10 PM'},
            {'slot_number': 5, 'start_time': '13:10', 'end_time': '14:00', 'label': '01:10 PM - 02:00 PM'},
            {'slot_number': 6, 'start_time': '14:00', 'end_time': '15:00', 'label': '02:00 PM - 03:00 PM'},
            {'slot_number': 7, 'start_time': '15:00', 'end_time': '16:00', 'label': '03:00 PM - 04:00 PM'},
        ]

        time_slots = {}
        for slot_data in time_slots_data:
            slot, created = TimeSlot.objects.get_or_create(
                slot_number=slot_data['slot_number'],
                defaults=slot_data
            )
            time_slots[slot.slot_number] = slot
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {slot}')

# ========== GET SECTION CS21 ==========
# Section name format: CS{semester}{section_num} e.g., CS31 for semester 3, section 1
try:
    section = Section.objects.get(name='CS31')
    self.stdout.write(f'\n  Found section: {section}')
except Section.DoesNotExist:
    # Try alternative names
    section = Section.objects.filter(name__startswith='CS', semester=3).first()
    if section:
        self.stdout.write(f'\n  Found section: {section}')
    else:
        self.stdout.write(self.style.ERROR('  Section CS31 not found! Run seedaktu first.'))
        return

        # ========== GET SUBJECTS ==========
        subjects = {}
        subject_codes = ['BCS301', 'BCS302', 'BCS303', 'BCC302', 'BAS303', 'BCS351', 'BCS352', 'BAS301', 'BCS353', 'BCC351']
        
        for code in subject_codes:
            try:
                # Try to find by code (AKTU code or BCS code)
                subj = Subject.objects.filter(code__icontains=code.replace('BCS', 'KCS').replace('BCC', 'KNC').replace('BAS', 'KAS')).first()
                if not subj:
                    subj = Subject.objects.filter(code__icontains=code).first()
                if subj:
                    subjects[code] = subj
                    self.stdout.write(f'  Found subject: {subj}')
            except Exception as e:
                self.stdout.write(f'  Warning: Subject {code} not found')

        # ========== CS21 TIMETABLE DATA ==========
        # Based on the image provided by user
        # Format: (day_of_week, slot_number, subject_code, lecture_type, room)
        
        timetable_data = [
            # MONDAY (day=0)
            (0, 1, 'BCS302', 'LECTURE', 'FLOOR-1/A-201'),   # Computer Organization
            (0, 2, 'BCS303', 'LECTURE', 'FLOOR-1/A-201'),   # Discrete Structures
            (0, 3, 'BCC302', 'LECTURE', 'FLOOR-1/A-201'),   # Python Prog
            (0, 4, 'BAS303', 'LECTURE', 'FLOOR-1/A-201'),   # Maths IV
            (0, 5, None, 'LUNCH', ''),                       # LUNCH
            (0, 6, 'BCS351', 'LAB', 'GROUND FLOOR/A-110'),  # DS Lab
            (0, 7, 'BCS351', 'LAB', 'GROUND FLOOR/A-110'),  # DS Lab

            # TUESDAY (day=1)
            (1, 1, 'BCS302', 'LECTURE', 'FLOOR-1/A-201'),   # Computer Organization
            (1, 2, 'BCS303', 'LECTURE', 'FLOOR-1/A-201'),   # Discrete Structures
            (1, 3, 'BCC302', 'LECTURE', 'FLOOR-1/A-201'),   # Python Prog
            (1, 4, 'BCS301', 'LECTURE', 'FLOOR-1/A-201'),   # Data Structure
            (1, 5, None, 'LUNCH', ''),                       # LUNCH
            (1, 6, 'BAS301', 'LECTURE', 'FLOOR-1/A-201'),   # Technical Communication
            (1, 7, 'BAS303', 'LECTURE', 'FLOOR-1/A-201'),   # Maths IV

            # WEDNESDAY (day=2)
            (2, 1, 'BCS302', 'LECTURE', 'FLOOR-1/A-201'),   # Computer Organization
            (2, 2, 'BCS301', 'LECTURE', 'FLOOR-1/A-201'),   # Data Structure
            (2, 3, 'BCS353', 'LAB', 'GROUND FLOOR/A-110'),  # Web Design Lab
            (2, 4, 'BCS353', 'LAB', 'GROUND FLOOR/A-110'),  # Web Design Lab
            (2, 5, None, 'LUNCH', ''),                       # LUNCH
            (2, 6, 'BAS303', 'LECTURE', 'FLOOR-1/A-201'),   # Maths IV
            (2, 7, 'BCC302', 'LECTURE', 'FLOOR-1/A-201'),   # Python Prog

            # THURSDAY (day=3)
            (3, 1, 'BCS302', 'LECTURE', 'FLOOR-1/A-201'),   # Computer Organization
            (3, 2, 'BCS303', 'LECTURE', 'FLOOR-1/A-201'),   # Discrete Structures
            (3, 3, 'BAS303', 'LECTURE', 'FLOOR-1/A-201'),   # Maths IV
            (3, 4, 'BCS301', 'LECTURE', 'FLOOR-1/A-201'),   # Data Structure
            (3, 5, None, 'LUNCH', ''),                       # LUNCH
            (3, 6, 'BAS301', 'LECTURE', 'FLOOR-1/A-201'),   # Technical Communication
            (3, 7, 'BAS303', 'LECTURE', 'FLOOR-1/A-201'),   # Maths IV

            # FRIDAY (day=4)
            (4, 1, 'BCC351', 'LAB', 'GROUND FLOOR/A-110'),  # Internship Assessment
            (4, 2, 'BCC351', 'LAB', 'GROUND FLOOR/A-110'),  # Internship Assessment
            (4, 3, 'BCS303', 'LECTURE', 'FLOOR-1/A-201'),   # Discrete Structures
            (4, 4, 'BCS301', 'LECTURE', 'FLOOR-1/A-201'),   # Data Structure
            (4, 5, None, 'LUNCH', ''),                       # LUNCH
            (4, 6, 'BAS303', 'LECTURE', 'FLOOR-1/A-201'),   # Maths IV

            # SATURDAY (day=5)
            (5, 1, 'BCS302', 'LECTURE', 'FLOOR-1/A-201'),   # Computer Organization
            (5, 2, 'BCS303', 'LECTURE', 'FLOOR-1/A-201'),   # Discrete Structures
            (5, 3, 'BAS303', 'LECTURE', 'FLOOR-1/A-201'),   # Maths IV
            (5, 4, 'BCS301', 'LECTURE', 'FLOOR-1/A-201'),   # Data Structure
            (5, 5, None, 'LUNCH', ''),                       # LUNCH
            (5, 6, 'BCS352', 'LAB', 'GROUND FLOOR/A-115'),  # CO Lab
            (5, 7, 'BCS352', 'LAB', 'GROUND FLOOR/A-115'),  # CO Lab
        ]

        # ========== CREATE TIMETABLE ENTRIES ==========
        created_count = 0
        for day, slot_num, subject_code, lec_type, room in timetable_data:
            subject = subjects.get(subject_code) if subject_code else None
            time_slot = time_slots.get(slot_num)

            if not time_slot:
                continue

            # Skip lunch breaks
            if lec_type == 'LUNCH':
                continue

            # If subject not found, skip (will be created manually later)
            if not subject:
                self.stdout.write(f'  Skipping: Subject {subject_code} not found')
                continue

            entry, created = Timetable.objects.get_or_create(
                day_of_week=day,
                time_slot=time_slot,
                section=section,
                defaults={
                    'subject': subject,
                    'lecture_type': lec_type,
                    'room': room,
                }
            )
            if created:
                created_count += 1
                day_name = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'][day]
                self.stdout.write(f'  Created: {day_name} {time_slot} - {subject.code} [{lec_type}]')

        # ========== FACULTY MAPPING (for reference) ==========
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write('FACULTY MAPPING (not added yet, for reference):')
        self.stdout.write('='*60)
        faculty_map = [
            ('BCS302', 'Computer Organization', 'MS. ANSHIKA YADAV'),
            ('BCS303', 'Discrete Structures', 'MR. DILEEP KUMAR GUPTA'),
            ('BCC302', 'Python Programming', 'MS. SARITA MAURYA'),
            ('BAS303', 'Maths IV', 'MR. ABHINAV VERMA'),
            ('BCS301', 'Data Structure', 'DR. ANITA PAL'),
            ('BAS301', 'Technical Communication', 'DR. MANJU SINGH'),
            ('BCS353', 'Web Design Workshop', 'MR. PANKAJ KUMAR GUPTA'),
            ('BCC351', 'Internship Assessment', 'MR. KAMAL NAYAN TIWARI'),
        ]
        for code, name, faculty in faculty_map:
            self.stdout.write(f'  {code} ({name}): {faculty}')

        # ========== SUMMARY ==========
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('CS21 TIMETABLE SEEDING COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Time Slots: {TimeSlot.objects.count()}')
        self.stdout.write(f'  Timetable Entries: {Timetable.objects.count()}')
        self.stdout.write(f'  New entries created: {created_count}')
        self.stdout.write(self.style.SUCCESS('='*60))
