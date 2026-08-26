from django.contrib import admin
from .models import FacultySubjectAssignment


@admin.register(FacultySubjectAssignment)
class FacultySubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['faculty', 'subject', 'section', 'academic_year', 'is_active']
    list_filter = ['academic_year', 'is_active', 'subject__department']
    search_fields = ['faculty__first_name', 'faculty__last_name', 'subject__code']
    raw_id_fields = ['faculty', 'subject', 'section']
