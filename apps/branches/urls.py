from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    path('', views.BranchListView.as_view(), name='branch_list'),
    path('create/', views.BranchCreateView.as_view(), name='branch_create'),
    path('<int:pk>/edit/', views.BranchUpdateView.as_view(), name='branch_edit'),
]
