from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Certificate
from audit_logs.models import VerificationHistory
from audit_logs.utils import get_client_ip

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_certificate_api(request):
    cert_num = request.query_params.get('certificate_number', '').strip()
    reg_num = request.query_params.get('register_number', '').strip()
    
    if not cert_num or not reg_num:
        return Response(
            {"error": "Both 'certificate_number' and 'register_number' query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        cert = Certificate.objects.select_related('student__user', 'course', 'department').get(
            certificate_number=cert_num,
            student__register_number=reg_num
        )
        
        # Check if the certificate is approved/verified
        if cert.status == 'APPROVED':
            if not cert.verification_date:
                cert.verification_date = timezone.now()
                cert.save(update_fields=['verification_date'])
                
            # Log successful search via API
            VerificationHistory.objects.create(
                searched_certificate_number=cert_num,
                searched_register_number=reg_num,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', 'Unknown') + " [REST API]",
                status='SUCCESS'
            )
            
            # Generate media absolute URIs safely
            qr_code_url = request.build_absolute_uri(cert.qr_code_image.url) if cert.qr_code_image else None
            pdf_url = request.build_absolute_uri(cert.pdf_file.url) if cert.pdf_file else None
            
            data = {
                "status": "verified",
                "certificate": {
                    "certificate_number": cert.certificate_number,
                    "register_number": cert.student.register_number,
                    "student_name": cert.student_name_snapshot,
                    "course": cert.course.name,
                    "department": cert.department.name,
                    "college_name": cert.student.college_name,
                    "university_name": cert.student.university_name,
                    "semester": cert.semester,
                    "cgpa": float(cert.cgpa),
                    "grade": cert.grade,
                    "issue_date": cert.issue_date.strftime('%Y-%m-%d'),
                    "expiry_date": cert.expiry_date.strftime('%Y-%m-%d') if cert.expiry_date else None,
                    "digital_signature": cert.digital_signature,
                    "qr_code_url": qr_code_url,
                    "pdf_url": pdf_url,
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            # Log failed API verification attempt due to status
            VerificationHistory.objects.create(
                searched_certificate_number=cert_num,
                searched_register_number=reg_num,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', 'Unknown') + " [REST API]",
                status='FAILED'
            )
            return Response(
                {"status": "not_found", "message": f"Certificate record found but status is '{cert.status}'."},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Certificate.DoesNotExist:
        # Log failed API search
        VerificationHistory.objects.create(
            searched_certificate_number=cert_num,
            searched_register_number=reg_num,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', 'Unknown') + " [REST API]",
            status='FAILED'
        )
        return Response(
            {"status": "not_found", "message": "Certificate record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
