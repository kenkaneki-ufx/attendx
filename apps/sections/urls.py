from django.urls import path
from . import views

app_name = 'sections'

urlpatterns = [
    path('', views.SectionListView.as_view(), name='section_list'),
    path('create/', views.SectionCreateView.as_view(), name='section_create'),
    path('<int:pk>/edit/', views.SectionUpdateView.as_view(), name='section_edit'),
]
