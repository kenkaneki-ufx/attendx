from django.test import TestCase, Client
from django.urls import reverse
from apps.departments.models import Department
from apps.branches.models import Branch
from apps.sections.models import Section
from apps.students.models import Student
from apps.accounts.models import Faculty
from apps.subjects.models import Subject
from apps.lectures.models import Lecture
from apps.attendance.models import AttendanceRecord
from apps.qr_codes.models import QRCodeSession
from django.utils import timezone
import secrets


class StudentPortalViewTest(TestCase):
    """Tests for the public student portal view."""

    def setUp(self):
        self.client = Client()
        self.portal_url = reverse('students:portal')
        self.department = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(
            department=self.department, name='CS', code='CS'
        )
        self.section = Section.objects.create(
            branch=self.branch, name='A', semester=6
        )
        self.student = Student.objects.create(
            registration_number='REG001',
            roll_number='CSE001',
            first_name='John',
            last_name='Doe',
            section=self.section,
            admission_year=2023,
        )

    def test_portal_loads(self):
        """Test portal page loads successfully."""
        response = self.client.get(self.portal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/portal.html')

    def test_portal_with_roll_number(self):
        """Test portal shows student data when roll number provided."""
        response = self.client.get(self.portal_url, {'roll_number': 'CSE001'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student'], self.student)

    def test_portal_with_invalid_roll_number(self):
        """Test portal shows error for invalid roll number."""
        response = self.client.get(self.portal_url, {'roll_number': 'INVALID'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_portal_with_inactive_student(self):
        """Test portal shows error for inactive student."""
        self.student.is_active = False
        self.student.save()
        response = self.client.get(self.portal_url, {'roll_number': 'CSE001'})
        self.assertIn('error', response.context)


class StudentLoginViewTest(TestCase):
    """Tests for the student login view."""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('students:student_login')
        self.department = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(
            department=self.department, name='CS', code='CS'
        )
        self.section = Section.objects.create(
            branch=self.branch, name='A', semester=6
        )
        self.student = Student.objects.create(
            registration_number='REG001',
            roll_number='CSE001',
            first_name='John',
            last_name='Doe',
            section=self.section,
            admission_year=2023,
        )
        self.student.set_password('testpass123')
        self.student.save()

    def test_login_page_loads(self):
        """Test login page loads."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/login.html')

    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(self.login_url, {
            'roll_number': 'CSE001',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('is_student'))

    def test_login_wrong_password(self):
        """Test login with wrong password."""
        response = self.client.post(self.login_url, {
            'roll_number': 'CSE001',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_nonexistent_student(self):
        """Test login with nonexistent roll number."""
        response = self.client.post(self.login_url, {
            'roll_number': 'INVALID',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)


class StudentDashboardViewTest(TestCase):
    """Tests for the student dashboard view."""

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('students:student_dashboard')
        self.department = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(
            department=self.department, name='CS', code='CS'
        )
        self.section = Section.objects.create(
            branch=self.branch, name='A', semester=6
        )
        self.student = Student.objects.create(
            registration_number='REG001',
            roll_number='CSE001',
            first_name='John',
            last_name='Doe',
            section=self.section,
            admission_year=2023,
        )
        self.student.set_password('testpass123')
        self.student.save()

        self.faculty = Faculty.objects.create_user(
            username='faculty1', email='faculty1@test.com', password='testpass123',
            first_name='Prof', last_name='Smith',
            employee_id='EMP001', department=self.department
        )
        self.subject = Subject.objects.create(
            name='Data Structures', code='CS201',
            department=self.department, semester=6
        )

    def _login_student(self):
        """Helper to login as student."""
        self.client.post(reverse('students:student_login'), {
            'roll_number': 'CSE001',
            'password': 'testpass123',
        })

    def test_dashboard_requires_login(self):
        """Test dashboard redirects when not logged in."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads(self):
        """Test dashboard loads for authenticated student."""
        self._login_student()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/dashboard.html')

    def test_dashboard_context_data(self):
        """Test dashboard provides correct context data."""
        self._login_student()
        response = self.client.get(self.dashboard_url)
        self.assertIn('student', response.context)
        self.assertIn('total_lectures', response.context)
        self.assertIn('attendance_rate', response.context)

    def test_dashboard_with_attendance(self):
        """Test dashboard displays attendance records."""
        self._login_student()
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
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.context['total_lectures'], 1)
        self.assertEqual(response.context['attendance_rate'], 100.0)


class StudentLogoutViewTest(TestCase):
    """Tests for student logout view."""

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('students:student_logout')
        self.department = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(
            department=self.department, name='CS', code='CS'
        )
        self.section = Section.objects.create(
            branch=self.branch, name='A', semester=6
        )
        self.student = Student.objects.create(
            registration_number='REG001',
            roll_number='CSE001',
            first_name='John',
            last_name='Doe',
            section=self.section,
            admission_year=2023,
        )
        self.student.set_password('testpass123')
        self.student.save()

    def test_logout_clears_session(self):
        """Test logout clears student session."""
        self.client.post(reverse('students:student_login'), {
            'roll_number': 'CSE001',
            'password': 'testpass123',
        })
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('is_student'))
