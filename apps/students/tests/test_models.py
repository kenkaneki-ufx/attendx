from django.test import TestCase
from apps.departments.models import Department
from apps.branches.models import Branch
from apps.sections.models import Section
from apps.students.models import Student


class StudentModelTest(TestCase):
    """Tests for the Student model."""

    def setUp(self):
        self.department = Department.objects.create(
            name='Computer Science', code='CSE'
        )
        self.branch = Branch.objects.create(
            department=self.department,
            name='Computer Science',
            code='CSE'
        )
        self.section = Section.objects.create(
            branch=self.branch,
            name='Section A',
            semester=6
        )
        self.student = Student.objects.create(
            registration_number='REG001',
            roll_number='CSE001',
            first_name='John',
            last_name='Doe',
            section=self.section,
            admission_year=2023,
        )

    def test_create_student(self):
        """Test creating a student."""
        self.assertEqual(self.student.roll_number, 'CSE001')
        self.assertEqual(self.student.first_name, 'John')
        self.assertEqual(self.student.last_name, 'Doe')
        self.assertEqual(self.student.section, self.section)
        self.assertTrue(self.student.is_active)

    def test_get_full_name(self):
        """Test get_full_name method."""
        self.assertEqual(self.student.get_full_name(), 'John Doe')

    def test_str_representation(self):
        """Test string representation."""
        self.assertEqual(str(self.student), 'John Doe (CSE001)')

    def test_roll_number_unique_per_section(self):
        """Test that roll number is unique per section."""
        with self.assertRaises(Exception):
            Student.objects.create(
                registration_number='REG002',
                roll_number='CSE001',
                first_name='Jane',
                last_name='Smith',
                section=self.section,
                admission_year=2023,
            )
