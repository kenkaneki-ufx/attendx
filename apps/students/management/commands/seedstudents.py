"""
Management command to seed CS21 students.
Run: python manage.py seedstudents
"""
from django.core.management.base import BaseCommand
from apps.students.models import Student
from apps.sections.models import Section


class Command(BaseCommand):
    help = 'Seed CS21 students from the provided list'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting CS21 student seeding...\n'))

        # Get section CS21
        try:
            section = Section.objects.get(name='CS21')
            self.stdout.write(f'  Found section: {section}')
        except Section.DoesNotExist:
            # Try to find any section starting with CS
            section = Section.objects.filter(name__startswith='CS', semester=3).first()
            if section:
                self.stdout.write(f'  Found section: {section}')
            else:
                self.stdout.write(self.style.ERROR('  Section CS21 not found! Run seedaktu first.'))
                return

        # Student data from user
        students_data = [
            {'name': 'ABHAY SINGH', 'code': '261800', 'email': ''},
            {'name': 'ABHISHEK KUMAR GUPTA', 'code': '260711', 'email': 'jais57923@gmail.com'},
            {'name': 'ABHISHEK KUMAR TRIPATHI', 'code': '260928', 'email': 'abhutripathi97@gmail.com'},
            {'name': 'ADITYA CHAUHAN', 'code': '261799', 'email': ''},
            {'name': 'AKHATAR ANSARI', 'code': '260285', 'email': ''},
            {'name': 'ANUSHKA SRIVASTAVA', 'code': '260753', 'email': ''},
            {'name': 'ARTI RAO', 'code': '260770', 'email': ''},
            {'name': 'AYUSH KUMAR MISHRA', 'code': '260997', 'email': ''},
            {'name': 'MANISHA KUMARI GUPTA', 'code': '261773', 'email': ''},
            {'name': 'SNEHA RASTOGI', 'code': '261749', 'email': ''},
            {'name': 'AARAV YADAV', 'code': '250829', 'email': 'aaravyt2000@gmail.com'},
            {'name': 'ABHAY GUPTA', 'code': '251994', 'email': ''},
            {'name': 'ABHAY KATIYAR', 'code': '252765', 'email': 'abhaykatiyar@gmail.com'},
            {'name': 'ABHAY KUMAR GUPTA', 'code': '252087', 'email': 'abhaykumargupta93055@gmail.com'},
            {'name': 'ABHAY NISHAD', 'code': '251222', 'email': 'abhaynishad5575@gmail.com'},
            {'name': 'ABHI YADAV', 'code': '250798', 'email': 'abhiyadavj2006@gmail.com'},
            {'name': 'ABHINAV SHARMA', 'code': '250229', 'email': 'karuneshsharma2018@gmail.com'},
            {'name': 'ABHINAV SRIVASTAV', 'code': '250320', 'email': 'abhinavsrivastav556@gmail.com'},
            {'name': 'ABHINAV TRIPATHI', 'code': '250586', 'email': 'abhinavtripathi1501@gmail.com'},
            {'name': 'ABHISHEK KUMAR YADAV', 'code': '251175', 'email': 'kumarabhishek281099@gmail.com'},
            {'name': 'ABHISHEK VISHWAKARMA', 'code': '250633', 'email': 'a85178221@gmail.com'},
            {'name': 'ABHISHEK YADAV', 'code': '251343', 'email': 'abhishekyadav955986@gmail.com'},
            {'name': 'ADARSH SINGH', 'code': '250194', 'email': 'asv6107@gmail.com'},
            {'name': 'ADARSH VERMA', 'code': '251046', 'email': 'adarshchoudhary0777@gmail.com'},
            {'name': 'ADITYA MISHRA', 'code': '251626', 'email': 'adityababa411@gmail.com'},
            {'name': 'ADITYA SINGH', 'code': '251688', 'email': 'singhaditya20070310@gmail.com'},
            {'name': 'ADITYA VERMA', 'code': '250373', 'email': ''},
            {'name': 'AHAMAD RAJJA ANSARI', 'code': '251020', 'email': 'ahamadraja202020@gmail.com'},
            {'name': 'AJEET YADAV', 'code': '251591', 'email': 'ajeetyadav972128@gmail.com'},
            {'name': 'AKANKSHA YADAV', 'code': '252741', 'email': 'akanksh.yadav10118@gmail.com'},
            {'name': 'AKSHAT SINGH', 'code': '250379', 'email': ''},
            {'name': 'ALOK SINGH', 'code': '252716', 'email': 'alok71548@gmail.com'},
            {'name': 'ALOK TRIVEDI', 'code': '250268', 'email': 'djaloktrivedi@gmail.com'},
            {'name': 'AMAN MAURYA', 'code': '250047', 'email': 'amanmaurya42011@gmail.com'},
            {'name': 'AMIT KUMAR', 'code': '250341', 'email': 'amit.samrat2872006@gmail.com'},
            {'name': 'ANCHAL SINGH', 'code': '252161', 'email': 'sanketsingh1296@gmail.com'},
            {'name': 'ANKIT', 'code': '251579', 'email': 'ankitch3980@gmail.com'},
            {'name': 'ANKIT GUPTA', 'code': '250364', 'email': 'ankitagraharibst718@gmail.com'},
            {'name': 'ANKIT MAURYA', 'code': '250046', 'email': 'shaileshmaurya059@gmail.com'},
            {'name': 'ANKIT PANDEY', 'code': '251853', 'email': 'ankitpandeyankitpandey392@gmail.com'},
            {'name': 'ANKIT PATEL', 'code': '251863', 'email': ''},
            {'name': 'ANKIT SINGH', 'code': '251322', 'email': ''},
            {'name': 'ANKIT SINGH', 'code': '252688', 'email': 'ankitsinghrajput332@gmail.com'},
            {'name': 'ANKIT YADAV', 'code': '251072', 'email': 'ay1234solutionnikhil567@gmail.com'},
            {'name': 'ANKUL RAJBHAR', 'code': '250881', 'email': 'ankulrajbhar917@gmail.com'},
            {'name': 'ANSH PANDEY', 'code': '252683', 'email': 'anshbhai2700@gmail.com'},
            {'name': 'ANSH SINGH', 'code': '250013', 'email': ''},
            {'name': 'ANSHIKA', 'code': '250232', 'email': ''},
            {'name': 'ANSHIKA DUBEY', 'code': '250577', 'email': 'dubeyanshika119@gmail.com'},
            {'name': 'ANUJ VERMA', 'code': '250331', 'email': ''},
            {'name': 'ANUSHKA VERMA', 'code': '252686', 'email': 'vanushka626@gmail.com'},
            {'name': 'ANUSHTHA TRIPATHI', 'code': '251209', 'email': 'anushtahatripathi2145@gmail.com'},
            {'name': 'AREEBA', 'code': '250092', 'email': 'sabeenak594@gmail.com'},
            {'name': 'ARPIT KUMAR SINGH', 'code': '250444', 'email': 'arpittsingh2006@gmail.com'},
            {'name': 'ARUN KUMAR', 'code': '250960', 'email': 'arunkumar06631@gmail.com'},
            {'name': 'ARYAN MAURYA', 'code': '251253', 'email': 'mauryaaryan6390@gmail.com'},
            {'name': 'ARYAN MISHRA', 'code': '250698', 'email': ''},
            {'name': 'ASHISH KUMAR SINGH', 'code': '250638', 'email': ''},
            {'name': 'ASHISH PRAJAPATI', 'code': '251526', 'email': 'ashishchakarwarti2731@gmail.com'},
            {'name': 'AVANISH KUMAR NISHAD', 'code': '250119', 'email': 'avanishkumar4321st@gmail.com'},
            {'name': 'AVINASH KUSHWAHA', 'code': '250400', 'email': 'avinashkushwahaplus999@gmail.com'},
            {'name': 'AWADH BIHARI SINGH', 'code': '251596', 'email': ''},
            {'name': 'AYUSH BISHT', 'code': '250258', 'email': ''},
            {'name': 'AYUSH SINGH', 'code': '252075', 'email': 'ayushsingh639420@gmail.com'},
            {'name': 'AYUSHI MAURYA', 'code': '250110', 'email': ''},
            {'name': 'CHANDAN KUSHWAHA', 'code': '250775', 'email': 'chandan.kus9156@gmail.com'},
            {'name': 'DEEPAK YADAV', 'code': '250124', 'email': ''},
            {'name': 'DEEPENDRA MISHRA', 'code': '250635', 'email': 'mdeependra754@gmail.com'},
            {'name': 'DEVANJALI YADAV', 'code': '251901', 'email': 'devanjaliya2@gmail.com'},
            {'name': 'DHRUV MISHRA', 'code': '250817', 'email': 'mishradhruv1912@gmail.com'},
            {'name': 'DIVAKAR VERMA', 'code': '250084', 'email': 'divakarverma024@gmail.com'},
            {'name': 'DIVYA YADAV', 'code': '250241', 'email': ''},
            {'name': 'FAIJAL ALAM', 'code': '250348', 'email': 'faijalalam444@gmail.com'},
            {'name': 'FAISAL RAZA', 'code': '250892', 'email': 'mrfaisalsiddiqui0@gmail.com'},
            {'name': 'FASIHUZZAMA', 'code': '250178', 'email': 'sahidakhatoon4228@gmail.com'},
            {'name': 'GOPAL YADAV', 'code': '250809', 'email': ''},
            {'name': 'MOHD SHADAB SIDDIQUI', 'code': '252717', 'email': 'shaikhshadab7084@gmail.com'},
            {'name': 'VINEET', 'code': '252756', 'email': ''},
        ]

        created_count = 0
        for data in students_data:
            # Parse name
            name_parts = data['name'].split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Determine admission year from code
            admission_year = 2025 if data['code'].startswith('25') else 2026
            
            student, created = Student.objects.get_or_create(
                roll_number=data['code'],
                section=section,
                defaults={
                    'registration_number': data['code'],
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': data['email'] if data['email'] else None,
                    'admission_year': admission_year,
                    'is_active': True,
                }
            )
            
            if created:
                # Set default password
                student.set_password('student123')
                created_count += 1
                self.stdout.write(f'  Created: {student.get_full_name()} ({student.roll_number})')
            else:
                self.stdout.write(f'  Exists: {student.get_full_name()} ({student.roll_number})')

        # ========== SUMMARY ==========
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('CS21 STUDENT SEEDING COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'  Total Students in CS21: {Student.objects.filter(section=section).count()}')
        self.stdout.write(f'  New created: {created_count}')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\nDefault password for all students: student123')
