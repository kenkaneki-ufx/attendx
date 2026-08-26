"""
Performance tests for AttendX - Testing with large datasets.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.departments.models import Department
from apps.branches.models import Branch
from apps.sections.models import Section
from apps.subjects.models import Subject
from apps.students.models import Student
from apps.accounts.models import Faculty
from apps.lectures.models import Lecture
from apps.attendance.models import AttendanceRecord
from apps.qr_codes.models import QRCodeSession
import time
import secrets

User = get_user_model()


class QueryPerformanceTest(TestCase):
    """Performance tests for database queries."""

    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(
            department=self.department, name='CS', code='CS'
        )
        self.section = Section.objects.create(
            branch=self.branch, name='A', semester=6
        )
        self.faculty = Faculty.objects.create_user(
            username='faculty1', email='faculty1@test.com', password='testpass123',
            first_name='Prof', last_name='Smith',
            employee_id='EMP001', department=self.department
        )
        self.subject = Subject.objects.create(
            name='Data Structures', code='CS201',
            department=self.department, semester=6
        )

        # Create 100 students
        self.students = []
        for i in range(100):
            student = Student.objects.create(
                registration_number=f'REG{i:04d}',
                roll_number=f'CSE{i:04d}',
                first_name=f'Student{i}',
                last_name='Test',
                section=self.section,
                admission_year=2023
            )
            self.students.append(student)

        # Create 50 lectures with attendance records
        self.lectures = []
        for i in range(50):
            lecture = Lecture.objects.create(
                subject=self.subject, faculty=self.faculty,
                section=self.section, lecture_number=i + 1,
                lecture_date=timezone.now().date() - timezone.timedelta(days=i),
                start_time=timezone.now() - timezone.timedelta(hours=1),
                end_time=timezone.now(),
                status='COMPLETED'
            )
            self.lectures.append(lecture)

            # Create QR session for each lecture
            qr_session = QRCodeSession.objects.create(
                lecture=lecture, token=secrets.token_urlsafe(32),
                secret_key=secrets.token_hex(64),
                expires_at=timezone.now() + timezone.timedelta(seconds=60)
            )

            # Create attendance records for each lecture
            for student in self.students[:50]:
                AttendanceRecord.objects.create(
                    student=student, lecture=lecture, qr_session=qr_session,
                    status='PRESENT' if i % 3 != 0 else 'ABSENT'
                )

    def test_student_portal_query_performance(self):
        """Test student portal query performance with many records."""
        start_time = time.time()
        response = self.client.get(
            reverse('students:portal'), {'roll_number': 'CSE0001'}
        )
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        query_time = end_time - start_time
        self.assertLess(query_time, 2.0, "Portal query took too long")

    def test_dashboard_query_performance(self):
        """Test faculty dashboard query performance."""
        self.client.login(username='faculty1', password='testpass123')

        start_time = time.time()
        response = self.client.get(reverse('dashboard:faculty_dashboard'))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        query_time = end_time - start_time
        self.assertLess(query_time, 2.0, "Dashboard query took too long")

    def test_reports_query_performance(self):
        """Test reports query performance with many records."""
        self.client.login(username='faculty1', password='testpass123')

        start_time = time.time()
        response = self.client.get(reverse('reports:daily_report'))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        query_time = end_time - start_time
        self.assertLess(query_time, 2.0, "Reports query took too long")

    def test_analytics_query_performance(self):
        """Test analytics dashboard query performance."""
        self.client.login(username='faculty1', password='testpass123')

        start_time = time.time()
        response = self.client.get(reverse('analytics:dashboard'))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        query_time = end_time - start_time
        self.assertLess(query_time, 3.0, "Analytics query took too long")

    def test_csv_export_performance(self):
        """Test CSV export performance with many records."""
        self.client.login(username='faculty1', password='testpass123')

        start_time = time.time()
        response = self.client.get(reverse('reports:export_attendance_csv'))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        query_time = end_time - start_time
        self.assertLess(query_time, 3.0, "CSV export took too long")
