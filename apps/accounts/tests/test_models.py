from django.test import TestCase
from django.contrib.auth import get_user_model

Faculty = get_user_model()


class FacultyModelTest(TestCase):
    """Tests for the Faculty (User) model."""

    def setUp(self):
        self.faculty = Faculty.objects.create_user(
            username='testfaculty',
            email='test@attendx.com',
            password='testpass123',
            first_name='Test',
            last_name='Faculty',
            employee_id='TST001',
        )

    def test_create_user(self):
        """Test creating a new faculty user."""
        self.assertEqual(self.faculty.username, 'testfaculty')
        self.assertEqual(self.faculty.email, 'test@attendx.com')
        self.assertEqual(self.faculty.first_name, 'Test')
        self.assertEqual(self.faculty.last_name, 'Faculty')
        self.assertEqual(self.faculty.employee_id, 'TST001')
        self.assertTrue(self.faculty.check_password('testpass123'))
        self.assertTrue(self.faculty.is_active)
        self.assertFalse(self.faculty.is_staff)
        self.assertFalse(self.faculty.is_admin)

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = Faculty.objects.create_superuser(
            username='admin',
            email='admin@attendx.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            employee_id='ADM001',
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_admin)

    def test_get_full_name(self):
        """Test get_full_name method."""
        self.assertEqual(self.faculty.get_full_name(), 'Test Faculty')

    def test_get_short_name(self):
        """Test get_short_name method."""
        self.assertEqual(self.faculty.get_short_name(), 'Test')

    def test_str_representation(self):
        """Test string representation."""
        self.assertEqual(str(self.faculty), 'Test Faculty (TST001)')

    def test_username_unique(self):
        """Test that username must be unique."""
        with self.assertRaises(Exception):
            Faculty.objects.create_user(
                username='testfaculty',
                email='another@attendx.com',
                password='testpass123',
                first_name='Another',
                last_name='User',
                employee_id='TST002',
            )

    def test_email_required(self):
        """Test that email is required."""
        with self.assertRaises(ValueError):
            Faculty.objects.create_user(
                username='noemail',
                email='',
                password='testpass123',
                first_name='No',
                last_name='Email',
                employee_id='TST003',
            )
