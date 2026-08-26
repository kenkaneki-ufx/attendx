from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.FacultyLoginView.as_view(), name='login'),
    path('logout/', views.FacultyLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.ResetPasswordView.as_view(), name='reset_password'),
]
