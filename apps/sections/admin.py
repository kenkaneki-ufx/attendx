from django.contrib import admin
from .models import Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'semester', 'is_active', 'created_at']
    list_filter = ['branch', 'semester', 'is_active']
    search_fields = ['name']
    ordering = ['branch', 'semester', 'name']
