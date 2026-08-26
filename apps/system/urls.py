from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('settings/', views.SystemSettingsView.as_view(), name='settings'),
]
