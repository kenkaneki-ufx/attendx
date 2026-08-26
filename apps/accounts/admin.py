from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

Faculty = get_user_model()


@admin.register(Faculty)
class FacultyAdmin(UserAdmin):
    model = Faculty
    list_display = ['username', 'email', 'first_name', 'last_name', 'employee_id', 'department', 'is_active', 'is_admin']
    list_filter = ['is_active', 'is_admin', 'department']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'employee_id', 'department', 'profile_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'employee_id', 'password1', 'password2'),
        }),
    )
