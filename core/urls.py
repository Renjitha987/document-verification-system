from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('verify/', views.verify_certificate, name='verify'),
    path('verify/download-report/<uuid:cert_id>/', views.download_verification_report, name='download_verification_report'),
]
