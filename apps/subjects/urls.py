from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.SubjectListView.as_view(), name='subject_list'),
    path('create/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('<int:pk>/edit/', views.SubjectUpdateView.as_view(), name='subject_edit'),
    path('assigned/', views.AssignedSubjectsView.as_view(), name='assigned_subjects'),
]
