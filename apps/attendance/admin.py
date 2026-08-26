from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'lecture', 'status', 'scan_time', 'ip_address']
    list_filter = ['status', 'lecture__lecture_date']
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_number']
    raw_id_fields = ['student', 'lecture', 'qr_session']
    readonly_fields = ['scan_time', 'ip_address', 'device_info']
