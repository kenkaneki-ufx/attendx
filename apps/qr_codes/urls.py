from django.urls import path
from . import views

app_name = 'qr_codes'

urlpatterns = [
    path('generate/', views.GenerateQRView.as_view(), name='generate'),
    path('display/', views.QRDisplayView.as_view(), name='display'),
    path('api/regenerate/', views.qr_regenerate_api, name='regenerate_api'),
]
