from django.contrib import admin, messages
from django.db import transaction
from .models import Lecture


def reset_faculty_data(modeladmin, request, queryset):
    """Admin action to reset all data for selected faculty members."""
    # Get unique faculty from selected lectures
    faculty_ids = queryset.values_list('faculty_id', flat=True).distinct()
    
    if not faculty_ids:
        modeladmin.message_user(request, 'No lectures selected.', messages.WARNING)
        return
    
    from apps.accounts.models import Faculty
    from apps.attendance.models import AttendanceRecord
    from apps.qr_codes.models import QRCodeSession
    
    total_lectures = 0
    total_attendance = 0
    total_qr = 0
    
    with transaction.atomic():
        for faculty_id in faculty_ids:
            try:
                faculty = Faculty.objects.get(pk=faculty_id)
            except Faculty.DoesNotExist:
                continue
            
            # Get all lectures by this faculty
            faculty_lectures = Lecture.objects.filter(faculty=faculty)
            lecture_count = faculty_lectures.count()
            
            # Delete attendance records
            attendance_count, _ = AttendanceRecord.objects.filter(
                lecture__faculty=faculty
            ).delete()
            
            # Delete QR sessions
            qr_count, _ = QRCodeSession.objects.filter(
                lecture__faculty=faculty
            ).delete()
            
            # Delete lectures
            faculty_lectures.delete()
            
            total_lectures += lecture_count
            total_attendance += attendance_count
            total_qr += qr_count
    
    modeladmin.message_user(
        request,
        f'Successfully deleted {total_lectures} lectures, {total_attendance} attendance records, and {total_qr} QR sessions.',
        messages.SUCCESS
    )


reset_faculty_data.short_description = 'Reset all data for faculty in selected lectures'


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ['subject', 'section', 'faculty', 'lecture_date', 'lecture_number', 'status']
    list_filter = ['status', 'lecture_date', 'subject__department']
    search_fields = ['subject__code', 'subject__name', 'faculty__first_name']
    raw_id_fields = ['faculty', 'subject', 'section']
    date_hierarchy = 'lecture_date'
    actions = [reset_faculty_data]
