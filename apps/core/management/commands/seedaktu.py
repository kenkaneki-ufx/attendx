"""
Management command to seed AKTU syllabus data.
Run: python manage.py seedaktu
"""
from django.core.management.base import BaseCommand
from apps.departments.models import Department
from apps.branches.models import Branch
from apps.sections.models import Section
from apps.subjects.models import Subject


class Command(BaseCommand):
    help = 'Seed database with AKTU BTech CSE syllabus data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting AKTU data seeding...\n'))

        # ========== DEPARTMENTS ==========
        departments_data = [
            {'name': 'Computer Science and Engineering', 'code': 'CSE', 'description': 'Department of Computer Science and Engineering'},
            {'name': 'Electronics and Communication Engineering', 'code': 'ECE', 'description': 'Department of Electronics and Communication Engineering'},
            {'name': 'Mechanical Engineering', 'code': 'ME', 'description': 'Department of Mechanical Engineering'},
            {'name': 'Civil Engineering', 'code': 'CE', 'description': 'Department of Civil Engineering'},
            {'name': 'Electrical Engineering', 'code': 'EE', 'description': 'Department of Electrical Engineering'},
            {'name': 'Information Technology', 'code': 'IT', 'description': 'Department of Information Technology'},
            {'name': 'Chemical Engineering', 'code': 'CHE', 'description': 'Department of Chemical Engineering'},
            {'name': 'Biotechnology', 'code': 'BT', 'description': 'Department of Biotechnology'},
        ]

        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            departments[dept.code] = dept
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {dept}')

        # ========== BRANCHES (CSE Specializations) ==========
        cse_dept = departments['CSE']
        branches_data = [
            {'name': 'Computer Science and Engineering', 'code': 'CSE'},
            {'name': 'CSE (Artificial Intelligence)', 'code': 'CSE-AI'},
            {'name': 'CSE (AI & Machine Learning)', 'code': 'CSE-ML'},
            {'name': 'CSE (Data Science)', 'code': 'CSE-DS'},
            {'name': 'CSE (Internet of Things)', 'code': 'CSE-IoT'},
            {'name': 'CSE (Cyber Security)', 'code': 'CSE-CS'},
            {'name': 'CSE (Cloud Computing)', 'code': 'CSE-CC'},
        ]

        branches = {}
        for branch_data in branches_data:
            branch, created = Branch.objects.get_or_create(
                department=cse_dept,
                code=branch_data['code'],
                defaults={'name': branch_data['name']}
            )
            branches[branch.code] = branch
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {branch}')

        # ========== SECTIONS ==========
        # Create sections for CSE branches: CS21, CS22, CS23, CS24 for semesters 3-8
        section_count = 0
        for branch_code, branch in branches.items():
            for semester in range(3, 9):  # Semesters 3 to 8
                for section_num in range(1, 5):  # 4 sections each
                    section_name = f'{branch_code.replace("-", "")}{semester}{section_num}'
                    # Shorter format: CS21, CS22, etc.
                    if branch_code == 'CSE':
                        section_name = f'CS{semester}{section_num}'
                    elif branch_code == 'CSE-AI':
                        section_name = f'AI{semester}{section_num}'
                    elif branch_code == 'CSE-ML':
                        section_name = f'ML{semester}{section_num}'
                    elif branch_code == 'CSE-DS':
                        section_name = f'DS{semester}{section_num}'
                    elif branch_code == 'CSE-IoT':
                        section_name = f'IoT{semester}{section_num}'
                    elif branch_code == 'CSE-CS':
                        section_name = f'CY{semester}{section_num}'
                    elif branch_code == 'CSE-CC':
                        section_name = f'CC{semester}{section_num}'

                    section, created = Section.objects.get_or_create(
                        branch=branch,
                        name=section_name,
                        semester=semester,
                    )
                    if created:
                        section_count += 1

        self.stdout.write(f'  Created {section_count} sections')

        # ========== SUBJECTS - SEMESTER III ==========
        sem3_subjects = [
            {'code': 'KAS302', 'name': 'Engineering Science Course / Maths IV', 'credits': 4},
            {'code': 'KAS301', 'name': 'Technical Communication', 'credits': 3},
            {'code': 'KCS301', 'name': 'Data Structures', 'credits': 4},
            {'code': 'KCS302', 'name': 'Computer Organization and Architecture', 'credits': 4},
            {'code': 'KCS303', 'name': 'Discrete Structures & Theory of Logic', 'credits': 3},
            {'code': 'KCS351', 'name': 'Data Structures Using C Lab', 'credits': 1},
            {'code': 'KCS352', 'name': 'Computer Organization Lab', 'credits': 1},
            {'code': 'KCS353', 'name': 'Discrete Structure & Logic Lab', 'credits': 1},
            {'code': 'KCS354', 'name': 'Mini Project / Internship Assessment', 'credits': 1},
            {'code': 'KNC301', 'name': 'Computer System Security', 'credits': 0},
            {'code': 'KNC302', 'name': 'Python Programming', 'credits': 0},
        ]

        # ========== SUBJECTS - SEMESTER IV ==========
        sem4_subjects = [
            {'code': 'KAS402', 'name': 'Maths IV / Engineering Science Course', 'credits': 4},
            {'code': 'KVE401', 'name': 'Universal Human Values', 'credits': 3},
            {'code': 'KCS401', 'name': 'Operating Systems', 'credits': 3},
            {'code': 'KCS402', 'name': 'Theory of Automata and Formal Languages', 'credits': 4},
            {'code': 'KCS403', 'name': 'Microprocessor', 'credits': 4},
            {'code': 'KCS451', 'name': 'Operating Systems Lab', 'credits': 1},
            {'code': 'KCS452', 'name': 'Microprocessor Lab', 'credits': 1},
            {'code': 'KCS453', 'name': 'Python Language Programming Lab', 'credits': 1},
            {'code': 'KNC402', 'name': 'Python Programming', 'credits': 0},
            {'code': 'KNC401', 'name': 'Computer System Security', 'credits': 0},
        ]

        # ========== SUBJECTS - SEMESTER V (Common CSE) ==========
        sem5_subjects = [
            {'code': 'KCS501', 'name': 'Design and Analysis of Algorithms', 'credits': 4},
            {'code': 'KCS502', 'name': 'Database Management Systems', 'credits': 4},
            {'code': 'KCS503', 'name': 'Computer Networks', 'credits': 3},
            {'code': 'KCS504', 'name': 'Software Engineering', 'credits': 3},
            {'code': 'KCS551', 'name': 'DBMS Lab', 'credits': 1},
            {'code': 'KCS552', 'name': 'Computer Networks Lab', 'credits': 1},
            {'code': 'KCS553', 'name': 'Mini Project I', 'credits': 2},
        ]

        # ========== SUBJECTS - SEMESTER VI (Common CSE) ==========
        sem6_subjects = [
            {'code': 'KCS601', 'name': 'Compiler Design', 'credits': 4},
            {'code': 'KCS602', 'name': 'Operating Systems', 'credits': 3},
            {'code': 'KCS603', 'name': 'Web Technologies', 'credits': 3},
            {'code': 'KCS604', 'name': 'Theory of Computation', 'credits': 3},
            {'code': 'KCS651', 'name': 'Compiler Design Lab', 'credits': 1},
            {'code': 'KCS652', 'name': 'Web Technologies Lab', 'credits': 1},
            {'code': 'KCS653', 'name': 'Mini Project II', 'credits': 2},
        ]

        # ========== SUBJECTS - SEMESTER VII ==========
        sem7_subjects = [
            {'code': 'KCS701', 'name': 'Machine Learning', 'credits': 4},
            {'code': 'KCS702', 'name': 'Cloud Computing', 'credits': 3},
            {'code': 'KCS703', 'name': 'Information Security', 'credits': 3},
            {'code': 'KCS751', 'name': 'Machine Learning Lab', 'credits': 1},
            {'code': 'KCS752', 'name': 'Cloud Computing Lab', 'credits': 1},
            {'code': 'KCS753', 'name': 'Major Project I', 'credits': 3},
        ]

        # ========== SUBJECTS - SEMESTER VIII ==========
        sem8_subjects = [
            {'code': 'KCS801', 'name': 'Internet of Things', 'credits': 3},
            {'code': 'KCS802', 'name': 'Big Data Analytics', 'credits': 3},
            {'code': 'KCS851', 'name': 'IoT Lab', 'credits': 1},
            {'code': 'KCS852', 'name': 'Big Data Analytics Lab', 'credits': 1},
            {'code': 'KCS853', 'name': 'Major Project II', 'credits': 6},
        ]

        all_semesters = {
            3: sem3_subjects,
            4: sem4_subjects,
            5: sem5_subjects,
            6: sem6_subjects,
            7: sem7_subjects,
            8: sem8_subjects,
        }

        subject_count = 0
        for semester, subjects in all_semesters.items():
            for subj_data in subjects:
                subject, created = Subject.objects.get_or_create(
                    code=subj_data['code'],
                    defaults={
                        'name': subj_data['name'],
                        'department': cse_dept,
                        'semester': semester,
                        'credits': subj_data['credits'],
                        'description': f'AKTU BTech CSE Semester {semester} subject',
                    }
                )
                if created:
                    subject_count += 1
                    self.stdout.write(f'  Created: {subject}')

        # ========== SUMMARY ==========
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('AKTU DATA SEEDING COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Departments: {Department.objects.count()}')
        self.stdout.write(f'  Branches: {Branch.objects.count()}')
        self.stdout.write(f'  Sections: {Section.objects.count()}')
        self.stdout.write(f'  Subjects: {Subject.objects.count()}')
        self.stdout.write(self.style.SUCCESS('='*60))
