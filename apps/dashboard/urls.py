from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.FacultyDashboardView.as_view(), name='faculty_dashboard'),
]
