from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('portal/', views.StudentPortalView.as_view(), name='portal'),
    path('login/', views.student_login_view, name='student_login'),
    path('logout/', views.student_logout_view, name='student_logout'),
    path('dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
]
