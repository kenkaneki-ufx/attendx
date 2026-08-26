from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.departments.models import Department
from apps.branches.models import Branch
from apps.sections.models import Section
from apps.subjects.models import Subject
from apps.students.models import Student
from apps.lectures.models import Lecture
from apps.qr_codes.models import QRCodeSession
from apps.attendance.models import AttendanceRecord

Faculty = get_user_model()


class AnalyticsDashboardViewTest(TestCase):
    """Tests for the analytics dashboard view."""

    def setUp(self):
        self.client = Client()
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@test.com', password='pass123',
            first_name='John', last_name='Doe', employee_id='F001'
        )
        self.dept = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(department=self.dept, name='CSE', code='CSE')
        self.section = Section.objects.create(branch=self.branch, name='A', semester=6)
        self.subject = Subject.objects.create(code='CS601', name='ML', department=self.dept, semester=6)
        self.student = Student.objects.create(
            registration_number='REG001', roll_number='CSE001',
            first_name='Jane', last_name='Smith',
            section=self.section, admission_year=2023
        )
        self.lecture = Lecture.objects.create(
            faculty=self.faculty, subject=self.subject,
            section=self.section, lecture_date=timezone.now().date(),
            lecture_number=1, start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            status='COMPLETED'
        )
        self.qr = QRCodeSession.create_session(self.lecture, 120)
        self.record = AttendanceRecord.objects.create(
            student=self.student, lecture=self.lecture,
            qr_session=self.qr, status='PRESENT'
        )

    def test_requires_login(self):
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_loads_for_authenticated(self):
        self.client.login(username='f1', password='pass123')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics')

    def test_context_has_stats(self):
        self.client.login(username='f1', password='pass123')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_present', response.context)
        self.assertIn('total_late', response.context)
        self.assertIn('total_absent', response.context)
        self.assertIn('attendance_rate', response.context)
        self.assertEqual(response.context['total_present'], 1)

    def test_context_has_chart_data(self):
        self.client.login(username='f1', password='pass123')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertIn('week_data', response.context)
        self.assertIn('subject_data', response.context)
        self.assertIn('section_data', response.context)
        self.assertIn('monthly_data', response.context)
        self.assertIn('top_students', response.context)
        self.assertIn('low_attendance_students', response.context)


class SubjectAnalyticsViewTest(TestCase):
    """Tests for the subject analytics view."""

    def setUp(self):
        self.client = Client()
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@test.com', password='pass123',
            first_name='John', last_name='Doe', employee_id='F001'
        )
        self.dept = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(department=self.dept, name='CSE', code='CSE')
        self.section = Section.objects.create(branch=self.branch, name='A', semester=6)
        self.subject = Subject.objects.create(code='CS601', name='ML', department=self.dept, semester=6)

    def test_requires_login(self):
        response = self.client.get(reverse('analytics:subject_analytics', kwargs={'subject_id': self.subject.pk}))
        self.assertEqual(response.status_code, 302)

    def test_loads_for_authenticated(self):
        self.client.login(username='f1', password='pass123')
        response = self.client.get(reverse('analytics:subject_analytics', kwargs={'subject_id': self.subject.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ML')

    def test_404_for_nonexistent_subject(self):
        self.client.login(username='f1', password='pass123')
        response = self.client.get(reverse('analytics:subject_analytics', kwargs={'subject_id': 9999}))
        self.assertEqual(response.status_code, 404)
