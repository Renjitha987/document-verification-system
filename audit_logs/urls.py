from django.urls import path
from . import views

urlpatterns = [
    path('admin/logs/', views.view_audit_logs, name='view_audit_logs'),
    path('admin/logs/verifications/', views.view_verification_logs, name='view_verification_logs'),
]
