from django.urls import path
from . import views

app_name = 'lectures'

urlpatterns = [
    path('', views.LectureListView.as_view(), name='lecture_list'),
    path('start/', views.StartLectureView.as_view(), name='start_lecture'),
    path('<int:pk>/', views.ActiveLectureView.as_view(), name='active_lecture'),
    path('<int:pk>/end/', views.EndLectureView.as_view(), name='end_lecture'),
]
