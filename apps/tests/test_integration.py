"""
Integration tests for AttendX - Full QR scan flow and cross-app interactions.
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
from apps.qr_codes.models import QRCodeSession
from apps.attendance.models import AttendanceRecord
import secrets

User = get_user_model()


class QRCodeScanFlowTest(TestCase):
    """Integration test for the complete QR code scan workflow."""

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
        self.student = Student.objects.create(
            registration_number='REG001', roll_number='CSE001',
            first_name='John', last_name='Doe',
            section=self.section, admission_year=2023
        )
        self.student.set_password('testpass123')
        self.student.save()

    def test_full_qr_scan_workflow(self):
        """Test complete workflow: start lecture -> generate QR -> scan -> end."""
        # Step 1: Faculty login
        self.client.login(username='faculty1', password='testpass123')

        # Step 2: Start a lecture
        lecture = Lecture.objects.create(
            subject=self.subject, faculty=self.faculty,
            section=self.section, lecture_number=1,
            lecture_date=timezone.now().date(), start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1), status='IN_PROGRESS'
        )

        # Step 3: Generate QR code
        token = secrets.token_urlsafe(32)
        qr_session = QRCodeSession.objects.create(
            lecture=lecture, token=token,
            secret_key=secrets.token_hex(64),
            expires_at=timezone.now() + timezone.timedelta(seconds=60)
        )

        # Step 4: Student scans QR code (using session-based auth)
        session = self.client.session
        session['is_student'] = True
        session['student_id'] = self.student.pk
        session.save()
        scan_url = reverse('attendance:scan_attendance', kwargs={'token': token})
        response = self.client.get(scan_url)
        self.assertEqual(response.status_code, 200)

        # Step 5: Verify attendance recorded
        self.assertTrue(
            AttendanceRecord.objects.filter(
                student=self.student, lecture=lecture
            ).exists()
        )

        # Step 6: End lecture
        lecture.status = 'COMPLETED'
        lecture.save()

        # Step 7: Verify lecture ended
        lecture.refresh_from_db()
        self.assertEqual(lecture.status, 'COMPLETED')


class CrossAppInteractionTest(TestCase):
    """Integration tests for cross-app interactions."""

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
        self.student = Student.objects.create(
            registration_number='REG001', roll_number='CSE001',
            first_name='John', last_name='Doe',
            section=self.section, admission_year=2023
        )
        self.student.set_password('testpass123')
        self.student.save()

    def test_dashboard_shows_lecture_stats(self):
        """Test faculty dashboard shows correct lecture statistics."""
        self.client.login(username='faculty1', password='testpass123')
        lecture = Lecture.objects.create(
            subject=self.subject, faculty=self.faculty,
            section=self.section, lecture_number=1,
            lecture_date=timezone.now().date(), start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1), status='COMPLETED'
        )
        qr_session = QRCodeSession.objects.create(
            lecture=lecture, token=secrets.token_urlsafe(32),
            secret_key=secrets.token_hex(64),
            expires_at=timezone.now() + timezone.timedelta(seconds=60)
        )
        AttendanceRecord.objects.create(
            student=self.student, lecture=lecture, qr_session=qr_session, status='PRESENT'
        )

        response = self.client.get(reverse('dashboard:faculty_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_lectures_today', response.context)

    def test_student_portal_shows_attendance(self):
        """Test student portal displays attendance records."""
        lecture = Lecture.objects.create(
            subject=self.subject, faculty=self.faculty,
            section=self.section, lecture_number=1,
            lecture_date=timezone.now().date(), start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1), status='COMPLETED'
        )
        qr_session = QRCodeSession.objects.create(
            lecture=lecture, token=secrets.token_urlsafe(32),
            secret_key=secrets.token_hex(64),
            expires_at=timezone.now() + timezone.timedelta(seconds=60)
        )
        AttendanceRecord.objects.create(
            student=self.student, lecture=lecture, qr_session=qr_session, status='PRESENT'
        )

        response = self.client.get(
            reverse('students:portal'), {'roll_number': 'CSE001'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_lectures'], 1)

    def test_reports_reflect_attendance_data(self):
        """Test reports correctly reflect attendance data."""
        self.client.login(username='faculty1', password='testpass123')
        lecture = Lecture.objects.create(
            subject=self.subject, faculty=self.faculty,
            section=self.section, lecture_number=1,
            lecture_date=timezone.now().date(), start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1), status='COMPLETED'
        )
        qr_session = QRCodeSession.objects.create(
            lecture=lecture, token=secrets.token_urlsafe(32),
            secret_key=secrets.token_hex(64),
            expires_at=timezone.now() + timezone.timedelta(seconds=60)
        )
        AttendanceRecord.objects.create(
            student=self.student, lecture=lecture, qr_session=qr_session, status='PRESENT'
        )

        response = self.client.get(reverse('reports:daily_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['report_data']) > 0)
