from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('daily/', views.DailyReportView.as_view(), name='daily_report'),
    path('weekly/', views.WeeklyReportView.as_view(), name='weekly_report'),
    path('monthly/', views.MonthlyReportView.as_view(), name='monthly_report'),
    path('export/daily/csv/', views.export_daily_csv, name='export_daily_csv'),
    path('export/daily/pdf/', views.export_daily_pdf, name='export_daily_pdf'),
    path('export/attendance/csv/', views.export_attendance_csv, name='export_attendance_csv'),
]
