from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('', views.FacultyListView.as_view(), name='faculty_list'),
    path('create/', views.FacultyCreateView.as_view(), name='faculty_create'),
    path('<int:pk>/edit/', views.FacultyUpdateView.as_view(), name='faculty_edit'),
    path('<int:pk>/toggle/', views.faculty_toggle_status, name='faculty_toggle'),
    path('assignments/', views.FacultySubjectAssignmentView.as_view(), name='assignments'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:pk>/delete/', views.delete_assignment, name='delete_assignment'),
]
