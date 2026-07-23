from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Departments
    path('admin/departments/', views.manage_departments, name='manage_departments'),
    path('admin/departments/add/', views.add_department, name='add_department'),
    path('admin/departments/delete/<int:pk>/', views.delete_department, name='delete_department'),
    
    # Courses
    path('admin/courses/', views.manage_courses, name='manage_courses'),
    path('admin/courses/add/', views.add_course, name='add_course'),
    path('admin/courses/delete/<int:pk>/', views.delete_course, name='delete_course'),
    
    # Students
    path('admin/students/', views.manage_students, name='manage_students'),
    path('admin/students/add/', views.add_student, name='add_student'),
    path('admin/students/edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('admin/students/delete/<int:pk>/', views.delete_student, name='delete_student'),
    
    # Certificates
    path('admin/certificates/', views.manage_certificates, name='manage_certificates'),
    path('admin/certificates/add/', views.add_certificate, name='add_certificate'),
    path('admin/certificates/edit/<uuid:pk>/', views.edit_certificate, name='edit_certificate'),
    path('admin/certificates/delete/<uuid:pk>/', views.delete_certificate, name='delete_certificate'),
    path('admin/certificates/<uuid:pk>/status/<str:status_choice>/', views.update_certificate_status, name='update_certificate_status'),
    
    # Export & Email Actions
    path('admin/certificates/export/excel/', views.export_certificates_excel, name='export_certificates_excel'),
    path('admin/certificates/export/pdf/', views.export_certificates_pdf, name='export_certificates_pdf'),
    path('admin/certificates/<uuid:pk>/email/', views.email_verification_report, name='email_verification_report'),
    
    # Verification REST API Endpoint
    path('api/v1/verify/', api.verify_certificate_api, name='verify_certificate_api'),
]
