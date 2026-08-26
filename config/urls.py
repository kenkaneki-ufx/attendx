"""
URL configuration for AttendX project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found
# Custom error handlers
def custom_404(request, exception):
    return page_not_found(request, exception, template_name='404.html')

handler404 = 'config.urls.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core app
    path('', include('apps.core.urls')),
    
    # Authentication
    path('accounts/', include('apps.accounts.urls')),
    
    # Dashboard
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Academic structure
    path('departments/', include('apps.departments.urls')),
    path('branches/', include('apps.branches.urls')),
    path('sections/', include('apps.sections.urls')),
    path('students/', include('apps.students.urls')),
    path('subjects/', include('apps.subjects.urls')),
    
    # Faculty
    path('faculty/', include('apps.faculty.urls')),
    
    # Lectures
    path('lectures/', include('apps.lectures.urls')),
    
    # Attendance
    path('attendance/', include('apps.attendance.urls')),
    
    # QR Codes
    path('qr/', include('apps.qr_codes.urls')),
    
    # Reports
    path('reports/', include('apps.reports.urls')),
    
    # Analytics
    path('analytics/', include('apps.analytics.urls')),
    
    # System settings
    path('system/', include('apps.system.urls')),
]

# Debug toolbar (development only)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
