from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.departments.models import Department
from apps.branches.models import Branch
from apps.sections.models import Section
from apps.subjects.models import Subject
from apps.students.models import Student
from apps.accounts.models import Faculty
from apps.lectures.models import Lecture
from apps.attendance.models import AttendanceRecord
from apps.qr_codes.models import QRCodeSession
from django.utils import timezone
import secrets

User = get_user_model()


class DailyReportViewTest(TestCase):
    """Tests for the daily report view."""

    def setUp(self):
        self.client = Client()
        self.daily_url = reverse('reports:daily_report')
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

    def test_daily_report_requires_login(self):
        """Test daily report requires authentication."""
        response = self.client.get(self.daily_url)
        self.assertEqual(response.status_code, 302)

    def test_daily_report_loads(self):
        """Test daily report loads for authenticated faculty."""
        self.client.login(username='faculty1', password='testpass123')
        response = self.client.get(self.daily_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/daily_report.html')

    def test_daily_report_context(self):
        """Test daily report provides correct context."""
        self.client.login(username='faculty1', password='testpass123')
        response = self.client.get(self.daily_url)
        self.assertIn('report_data', response.context)
        self.assertIn('report_date', response.context)


class WeeklyReportViewTest(TestCase):
    """Tests for the weekly report view."""

    def setUp(self):
        self.client = Client()
        self.weekly_url = reverse('reports:weekly_report')
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

    def test_weekly_report_requires_login(self):
        """Test weekly report requires authentication."""
        response = self.client.get(self.weekly_url)
        self.assertEqual(response.status_code, 302)

    def test_weekly_report_loads(self):
        """Test weekly report loads for authenticated faculty."""
        self.client.login(username='faculty1', password='testpass123')
        response = self.client.get(self.weekly_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/weekly_report.html')


class MonthlyReportViewTest(TestCase):
    """Tests for the monthly report view."""

    def setUp(self):
        self.client = Client()
        self.monthly_url = reverse('reports:monthly_report')
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

    def test_monthly_report_requires_login(self):
        """Test monthly report requires authentication."""
        response = self.client.get(self.monthly_url)
        self.assertEqual(response.status_code, 302)

    def test_monthly_report_loads(self):
        """Test monthly report loads for authenticated faculty."""
        self.client.login(username='faculty1', password='testpass123')
        response = self.client.get(self.monthly_url)
        self.assertEqual(response.status_code, 200)


class ExportDailyCSVTest(TestCase):
    """Tests for daily CSV export."""

    def setUp(self):
        self.client = Client()
        self.csv_url = reverse('reports:export_daily_csv')
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

    def test_csv_export_requires_login(self):
        """Test CSV export requires authentication."""
        response = self.client.get(self.csv_url)
        self.assertEqual(response.status_code, 302)

    def test_csv_export_empty(self):
        """Test CSV export with no lectures."""
        self.client.login(username='faculty1', password='testpass123')
        response = self.client.get(self.csv_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_csv_export_with_data(self):
        """Test CSV export with lecture data."""
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
        response = self.client.get(self.csv_url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('CS201', content)


class ExportAttendanceCSVTest(TestCase):
    """Tests for detailed attendance CSV export."""

    def setUp(self):
        self.client = Client()
        self.csv_url = reverse('reports:export_attendance_csv')
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

    def test_attendance_csv_requires_login(self):
        """Test attendance CSV export requires authentication."""
        response = self.client.get(self.csv_url)
        self.assertEqual(response.status_code, 302)

    def test_attendance_csv_export(self):
        """Test attendance CSV export with data."""
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
        response = self.client.get(self.csv_url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('CSE001', content)


class ExportDailyPDFTest(TestCase):
    """Tests for daily PDF export."""

    def setUp(self):
        self.client = Client()
        self.pdf_url = reverse('reports:export_daily_pdf')
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

    def test_pdf_export_requires_login(self):
        """Test PDF export requires authentication."""
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 302)

    def test_pdf_export_empty(self):
        """Test PDF export with no lectures."""
        self.client.login(username='faculty1', password='testpass123')
        response = self.client.get(self.pdf_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
