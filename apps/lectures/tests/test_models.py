from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.departments.models import Department
from apps.branches.models import Branch
from apps.sections.models import Section
from apps.subjects.models import Subject
from apps.students.models import Student
from apps.lectures.models import Lecture
from apps.attendance.models import AttendanceRecord
from apps.qr_codes.models import QRCodeSession
from django.contrib.auth import get_user_model

Faculty = get_user_model()


class LectureModelTest(TestCase):
    """Tests for the Lecture model."""

    def setUp(self):
        self.department = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(
            department=self.department, name='CSE', code='CSE'
        )
        self.section = Section.objects.create(
            branch=self.branch, name='Section A', semester=6
        )
        self.subject = Subject.objects.create(
            code='CS601', name='Machine Learning',
            department=self.department, semester=6
        )
        self.faculty = Faculty.objects.create_user(
            username='faculty1', email='f1@test.com',
            password='pass123', first_name='Raj', last_name='Kumar',
            employee_id='FAC001'
        )
        self.lecture = Lecture.objects.create(
            faculty=self.faculty,
            subject=self.subject,
            section=self.section,
            lecture_date=timezone.now().date(),
            lecture_number=1,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            status='IN_PROGRESS'
        )

    def test_create_lecture(self):
        """Test creating a lecture."""
        self.assertEqual(self.lecture.faculty, self.faculty)
        self.assertEqual(self.lecture.subject, self.subject)
        self.assertEqual(self.lecture.status, 'IN_PROGRESS')

    def test_start_lecture(self):
        """Test starting a lecture."""
        self.lecture.status = 'SCHEDULED'
        self.lecture.start()
        self.assertEqual(self.lecture.status, 'IN_PROGRESS')

    def test_end_lecture(self):
        """Test ending a lecture."""
        self.lecture.end()
        self.assertEqual(self.lecture.status, 'COMPLETED')

    def test_cancel_lecture(self):
        """Test cancelling a lecture."""
        self.lecture.cancel()
        self.assertEqual(self.lecture.status, 'CANCELLED')


class QRCodeSessionTest(TestCase):
    """Tests for the QRCodeSession model."""

    def setUp(self):
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
        self.lecture = Lecture.objects.create(
            faculty=self.faculty, subject=self.subject,
            section=self.section, lecture_date=timezone.now().date(),
            lecture_number=1, start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            status='IN_PROGRESS'
        )
        self.qr = QRCodeSession.create_session(self.lecture, 60)

    def test_create_session(self):
        """Test creating a QR session."""
        self.assertIsNotNone(self.qr.token)
        self.assertTrue(self.qr.is_active)

    def test_is_expired(self):
        """Test expiration check."""
        self.qr.expires_at = timezone.now() - timedelta(seconds=1)
        self.assertTrue(self.qr.is_expired())

    def test_deactivate(self):
        """Test deactivating a session."""
        self.qr.deactivate()
        self.assertFalse(self.qr.is_active)


class AttendanceRecordTest(TestCase):
    """Tests for the AttendanceRecord model."""

    def setUp(self):
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
        self.qr = QRCodeSession.create_session(self.lecture, 60)

    def test_mark_present(self):
        """Test marking a student present."""
        record, created = AttendanceRecord.mark_present(
            student=self.student,
            lecture=self.lecture,
            qr_session=self.qr
        )
        self.assertTrue(created)
        self.assertEqual(record.status, 'PRESENT')

    def test_duplicate_prevention(self):
        """Test that duplicate attendance is prevented."""
        AttendanceRecord.mark_present(
            student=self.student,
            lecture=self.lecture,
            qr_session=self.qr
        )
        record, created = AttendanceRecord.mark_present(
            student=self.student,
            lecture=self.lecture,
            qr_session=self.qr
        )
        self.assertFalse(created)

    def test_attendance_stats(self):
        """Test attendance statistics calculation."""
        AttendanceRecord.mark_present(
            student=self.student,
            lecture=self.lecture,
            qr_session=self.qr
        )
        stats = AttendanceRecord.get_attendance_stats(self.lecture)
        self.assertEqual(stats['present'], 1)
        self.assertEqual(stats['total'], 1)
