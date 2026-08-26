from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'first_name', 'last_name', 'section', 'registration_number', 'is_active']
    list_filter = ['section', 'is_active', 'admission_year']
    search_fields = ['roll_number', 'first_name', 'last_name', 'registration_number']
    ordering = ['section', 'roll_number']
