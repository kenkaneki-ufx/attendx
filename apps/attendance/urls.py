from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.LiveAttendanceView.as_view(), name='live_attendance'),
    path('history/', views.AttendanceHistoryView.as_view(), name='attendance_history'),
    path('scan/<str:token>/', views.scan_attendance, name='scan_attendance'),
    path('api/refresh/', views.attendance_refresh_api, name='refresh_api'),
]
