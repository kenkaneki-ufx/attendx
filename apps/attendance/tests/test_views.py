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


class AttendanceScanTest(TestCase):
    """Tests for the attendance scan endpoint."""

    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(
            department=self.department, name='CSE', code='CSE'
        )
        self.section = Section.objects.create(
            branch=self.branch, name='Section A', semester=6
        )
        self.subject = Subject.objects.create(
            code='CS601', name='ML', department=self.department, semester=6
        )
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@t.com', password='pass',
            first_name='R', last_name='K', employee_id='F001'
        )
        self.student = Student.objects.create(
            registration_number='REG001', roll_number='CSE001',
            first_name='John', last_name='Doe',
            section=self.section, admission_year=2023
        )
        self.lecture = Lecture.objects.create(
            faculty=self.faculty, subject=self.subject,
            section=self.section, lecture_date=timezone.now().date(),
            lecture_number=1, start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            status='IN_PROGRESS'
        )
        self.qr = QRCodeSession.create_session(self.lecture, 120)

    def _set_student_session(self):
        """Helper to set up student session."""
        session = self.client.session
        session['is_student'] = True
        session['student_id'] = self.student.pk
        session.save()

    def test_scan_page_loads(self):
        """Test scan page loads with token."""
        self._set_student_session()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_scan_invalid_token(self):
        """Test scan with invalid token."""
        url = reverse('attendance:scan_attendance', kwargs={'token': 'invalid-token'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid QR code')

    def test_scan_expired_token(self):
        """Test scan with expired token."""
        self.qr.expires_at = timezone.now() - timedelta(seconds=1)
        self.qr.save()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'expired')

    def test_scan_without_student_id(self):
        """Test scan without student session."""
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login as a student')

    def test_scan_success(self):
        """Test successful attendance scan."""
        self._set_student_session()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AttendanceRecord.objects.filter(
            student=self.student, lecture=self.lecture
        ).exists())

    def test_scan_duplicate(self):
        """Test duplicate scan shows already submitted."""
        AttendanceRecord.mark_present(
            student=self.student, lecture=self.lecture, qr_session=self.qr
        )
        self._set_student_session()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already submitted')

    def test_scan_wrong_section(self):
        """Test scan by student from wrong section."""
        # Create another section and student
        section2 = Section.objects.create(branch=self.branch, name='Section B', semester=6)
        student2 = Student.objects.create(
            registration_number='REG002', roll_number='CSE002',
            first_name='Jane', last_name='Doe',
            section=section2, admission_year=2023
        )
        session = self.client.session
        session['is_student'] = True
        session['student_id'] = student2.pk
        session.save()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not enrolled')

    def test_scan_inactive_student(self):
        """Test scan by inactive student."""
        self.student.is_active = False
        self.student.save()
        self._set_student_session()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student not found')

    def test_scan_lecture_not_in_progress(self):
        """Test scan when lecture is not in progress."""
        self.lecture.status = 'COMPLETED'
        self.lecture.save()
        self._set_student_session()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not currently active')

    def test_scan_rate_limiting(self):
        """Test rate limiting on scan endpoint."""
        from django.core.cache import cache
        ip_address = '127.0.0.1'
        rate_limit_key = f'scan_rate_{ip_address}'
        cache.set(rate_limit_key, 10, 60)
        self._set_student_session()
        url = reverse('attendance:scan_attendance', kwargs={'token': self.qr.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Too many scan attempts')
        cache.delete(rate_limit_key)


class LiveAttendanceViewTest(TestCase):
    """Tests for the live attendance view."""

    def setUp(self):
        self.client = Client()
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@t.com', password='pass',
            first_name='R', last_name='K', employee_id='F001'
        )

    def test_live_attendance_requires_login(self):
        """Test live attendance requires authentication."""
        response = self.client.get(reverse('attendance:live_attendance'))
        self.assertEqual(response.status_code, 302)

    def test_live_attendance_loads(self):
        """Test live attendance loads for authenticated user."""
        self.client.login(username='f1', password='pass')
        response = self.client.get(reverse('attendance:live_attendance'))
        self.assertEqual(response.status_code, 200)
