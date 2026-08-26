from django.contrib import admin
from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'semester', 'credits', 'is_active']
    list_filter = ['department', 'semester', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['department', 'semester', 'code']
