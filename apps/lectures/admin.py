from django.contrib import admin
from .models import Lecture


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ['subject', 'section', 'faculty', 'lecture_date', 'lecture_number', 'status']
    list_filter = ['status', 'lecture_date', 'subject__department']
    search_fields = ['subject__code', 'subject__name', 'faculty__first_name']
    raw_id_fields = ['faculty', 'subject', 'section']
    date_hierarchy = 'lecture_date'
