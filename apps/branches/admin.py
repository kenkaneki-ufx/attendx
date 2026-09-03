from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'is_active', 'created_at']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['department', 'name']
