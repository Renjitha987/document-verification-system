import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.db.models import Q
from certificates.models import Certificate
from certificates.utils import generate_verification_pdf
from audit_logs.models import VerificationHistory
from audit_logs.utils import get_client_ip

def home(request):
    return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # In a real app, send mail or store in database. Here we show a success message.
        messages.success(request, f"Thank you {name}, your message has been sent successfully. We will contact you shortly!")
        return redirect('contact')
        
    return render(request, 'core/contact.html')


def verify_certificate(request):
    cert_num = request.GET.get('certificate_number', '').strip()
    reg_num = request.GET.get('register_number', '').strip()
    
    certificate = None
    searched = False
    status_msg = ""
    status_class = ""
    
    if cert_num or reg_num:
        searched = True
        
        # Attempt to find the certificate matching both fields
        try:
            certificate = Certificate.objects.select_related('student__user', 'course', 'department').get(
                certificate_number=cert_num,
                student__register_number=reg_num
            )
            
            # Map status
            if certificate.status == 'APPROVED':
                # Set verification date if not already set, for tracking
                if not certificate.verification_date:
                    certificate.verification_date = timezone.now()
                    certificate.save(update_fields=['verification_date'])
                
                # Log success
                VerificationHistory.objects.create(
                    searched_certificate_number=cert_num,
                    searched_register_number=reg_num,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    status='SUCCESS'
                )
            else:
                # Log failed search due to revoked/rejected/pending status
                VerificationHistory.objects.create(
                    searched_certificate_number=cert_num,
                    searched_register_number=reg_num,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    status='FAILED'
                )
                
        except Certificate.DoesNotExist:
            certificate = None
            # Log failed search
            VerificationHistory.objects.create(
                searched_certificate_number=cert_num,
                searched_register_number=reg_num,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status='FAILED'
            )
            
    context = {
        'certificate': certificate,
        'searched': searched,
        'certificate_number': cert_num,
        'register_number': reg_num,
    }
    return render(request, 'core/verify.html', context)


def download_verification_report(request, cert_id):
    """Generates and serves a highly professional PDF verification report for a certificate."""
    cert = get_object_or_404(Certificate.objects.select_related('student__user', 'course', 'department'), id=cert_id)
    
    pdf_buffer = generate_verification_pdf(cert)
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="verification_report_{cert.certificate_number}.pdf"'
    return response
