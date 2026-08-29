from django.contrib import admin, messages
from django.db import transaction
from .models import AttendanceRecord


def reset_selected_faculty_attendance(modeladmin, request, queryset):
    """Admin action to reset attendance for faculty members from selected records."""
    # Get unique faculty from selected attendance records
    faculty_ids = queryset.values_list('lecture__faculty_id', flat=True).distinct()
    
    if not faculty_ids:
        modeladmin.message_user(request, 'No attendance records selected.', messages.WARNING)
        return
    
    from apps.accounts.models import Faculty
    from apps.lectures.models import Lecture
    from apps.qr_codes.models import QRCodeSession
    
    total_lectures = 0
    total_attendance = 0
    total_qr = 0
    
    with transaction.atomic():
        for faculty_id in faculty_ids:
            if not faculty_id:
                continue
            try:
                faculty = Faculty.objects.get(pk=faculty_id)
            except Faculty.DoesNotExist:
                continue
            
            # Delete attendance records for this faculty
            attendance_count, _ = AttendanceRecord.objects.filter(
                lecture__faculty=faculty
            ).delete()
            
            # Delete QR sessions
            qr_count, _ = QRCodeSession.objects.filter(
                lecture__faculty=faculty
            ).delete()
            
            # Delete lectures
            lecture_count, _ = Lecture.objects.filter(faculty=faculty).delete()
            
            total_lectures += lecture_count
            total_attendance += attendance_count
            total_qr += qr_count
    
    modeladmin.message_user(
        request,
        f'Successfully deleted {total_lectures} lectures, {total_attendance} attendance records, and {total_qr} QR sessions.',
        messages.SUCCESS
    )


reset_selected_faculty_attendance.short_description = 'Reset all data for faculty in selected records'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'lecture', 'status', 'scan_time', 'ip_address']
    list_filter = ['status', 'lecture__lecture_date']
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_number']
    raw_id_fields = ['student', 'lecture', 'qr_session']
    readonly_fields = ['scan_time', 'ip_address', 'device_info']
    actions = [reset_selected_faculty_attendance]
