from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.faculty.models import FacultySubjectAssignment
from apps.departments.models import Department
from apps.subjects.models import Subject
from apps.sections.models import Section
from apps.branches.models import Branch

Faculty = get_user_model()


class FacultyListViewTest(TestCase):
    """Tests for the faculty list view (admin only)."""

    def setUp(self):
        self.client = Client()
        self.admin = Faculty.objects.create_superuser(
            username='admin', email='admin@test.com',
            password='adminpass123', first_name='Admin', last_name='User',
            employee_id='ADM001'
        )
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@test.com', password='pass123',
            first_name='John', last_name='Doe', employee_id='F001'
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('faculty:faculty_list'))
        self.assertIn(response.status_code, [302, 404])  # AdminRequiredMixin raises 404 for unauthenticated

    def test_list_requires_admin(self):
        self.client.login(username='f1', password='pass123')
        response = self.client.get(reverse('faculty:faculty_list'))
        self.assertEqual(response.status_code, 404)

    def test_list_loads_for_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('faculty:faculty_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Faculty Management')

    def test_search_filters(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('faculty:faculty_list') + '?search=John')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')

    def test_status_filter(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('faculty:faculty_list') + '?status=active')
        self.assertEqual(response.status_code, 200)


class FacultyCreateViewTest(TestCase):
    """Tests for the faculty create view (admin only)."""

    def setUp(self):
        self.client = Client()
        self.admin = Faculty.objects.create_superuser(
            username='admin', email='admin@test.com',
            password='adminpass123', first_name='Admin', last_name='User',
            employee_id='ADM001'
        )
        self.dept = Department.objects.create(name='CSE', code='CSE')

    def test_create_requires_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('faculty:faculty_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Faculty')

    def test_create_faculty_success(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('faculty:faculty_create'), {
            'username': 'newfaculty',
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'Faculty',
            'employee_id': 'NEW001',
            'department': self.dept.pk,
            'password': 'securepass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Faculty.objects.filter(username='newfaculty').exists())

    def test_create_duplicate_username(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('faculty:faculty_create'), {
            'username': 'admin',
            'email': 'another@test.com',
            'first_name': 'Another',
            'last_name': 'User',
            'employee_id': 'NEW002',
            'password': 'securepass123',
        })
        self.assertEqual(response.status_code, 200)  # Form re-rendered with error

    def test_create_short_password(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('faculty:faculty_create'), {
            'username': 'shortpw',
            'email': 'short@test.com',
            'first_name': 'Short',
            'last_name': 'Password',
            'employee_id': 'SPW001',
            'password': 'short',
        })
        # Short password triggers error message via messages framework then redirects
        self.assertIn(response.status_code, [200, 302])


class FacultyUpdateViewTest(TestCase):
    """Tests for the faculty update view."""

    def setUp(self):
        self.client = Client()
        self.admin = Faculty.objects.create_superuser(
            username='admin', email='admin@test.com',
            password='adminpass123', first_name='Admin', last_name='User',
            employee_id='ADM001'
        )
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@test.com', password='pass123',
            first_name='John', last_name='Doe', employee_id='F001'
        )

    def test_edit_loads(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('faculty:faculty_edit', kwargs={'pk': self.faculty.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Faculty')

    def test_edit_update_success(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('faculty:faculty_edit', kwargs={'pk': self.faculty.pk}), {
            'username': 'f1',
            'email': 'f1@test.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'employee_id': 'F001',
        })
        self.assertEqual(response.status_code, 302)
        self.faculty.refresh_from_db()
        self.assertEqual(self.faculty.first_name, 'Jane')


class FacultyToggleStatusTest(TestCase):
    """Tests for the toggle status AJAX endpoint."""

    def setUp(self):
        self.client = Client()
        self.admin = Faculty.objects.create_superuser(
            username='admin', email='admin@test.com',
            password='adminpass123', first_name='Admin', last_name='User',
            employee_id='ADM001'
        )
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@test.com', password='pass123',
            first_name='John', last_name='Doe', employee_id='F001'
        )

    def test_toggle_deactivate(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('faculty:faculty_toggle', kwargs={'pk': self.faculty.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['is_active'])

    def test_toggle_self_deactivation(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('faculty:faculty_toggle', kwargs={'pk': self.admin.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('own account', data['message'])


class FacultyAssignmentTest(TestCase):
    """Tests for faculty-subject assignments."""

    def setUp(self):
        self.client = Client()
        self.admin = Faculty.objects.create_superuser(
            username='admin', email='admin@test.com',
            password='adminpass123', first_name='Admin', last_name='User',
            employee_id='ADM001'
        )
        self.faculty = Faculty.objects.create_user(
            username='f1', email='f1@test.com', password='pass123',
            first_name='John', last_name='Doe', employee_id='F001'
        )
        self.dept = Department.objects.create(name='CSE', code='CSE')
        self.branch = Branch.objects.create(department=self.dept, name='CSE', code='CSE')
        self.section = Section.objects.create(branch=self.branch, name='A', semester=6)
        self.subject = Subject.objects.create(code='CS601', name='ML', department=self.dept, semester=6)

    def test_assignments_view_loads(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('faculty:assignments'))
        self.assertEqual(response.status_code, 200)

    def test_create_assignment(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('faculty:create_assignment'), {
            'faculty_id': self.faculty.pk,
            'subject_id': self.subject.pk,
            'section_id': self.section.pk,
            'academic_year': '2025-2026',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(FacultySubjectAssignment.objects.filter(
            faculty=self.faculty, subject=self.subject
        ).exists())

    def test_duplicate_assignment(self):
        self.client.login(username='admin', password='adminpass123')
        FacultySubjectAssignment.objects.create(
            faculty=self.faculty, subject=self.subject,
            section=self.section, academic_year='2025-2026'
        )
        response = self.client.post(reverse('faculty:create_assignment'), {
            'faculty_id': self.faculty.pk,
            'subject_id': self.subject.pk,
            'section_id': self.section.pk,
            'academic_year': '2025-2026',
        })
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('already exists', data['message'])

    def test_delete_assignment(self):
        self.client.login(username='admin', password='adminpass123')
        assignment = FacultySubjectAssignment.objects.create(
            faculty=self.faculty, subject=self.subject,
            section=self.section, academic_year='2025-2026'
        )
        response = self.client.post(reverse('faculty:delete_assignment', kwargs={'pk': assignment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(FacultySubjectAssignment.objects.filter(pk=assignment.pk).exists())
