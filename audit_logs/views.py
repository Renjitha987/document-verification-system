from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import AuditLog, VerificationHistory
from django.contrib import messages

@login_required
def view_audit_logs(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('dashboard')
        
    query = request.GET.get('q', '').strip()
    logs_list = AuditLog.objects.select_related('user').all()
    
    if query:
        logs_list = logs_list.filter(
            Q(user__username__icontains=query) |
            Q(action__icontains=query) |
            Q(description__icontains=query) |
            Q(ip_address__icontains=query)
        )
        
    paginator = Paginator(logs_list, 20)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    
    return render(request, 'audit_logs/audit_logs.html', {'logs': logs, 'query': query})


@login_required
def view_verification_logs(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('dashboard')
        
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    logs_list = VerificationHistory.objects.all()
    
    if query:
        logs_list = logs_list.filter(
            Q(searched_certificate_number__icontains=query) |
            Q(searched_register_number__icontains=query) |
            Q(ip_address__icontains=query)
        )
        
    if status_filter:
        logs_list = logs_list.filter(status=status_filter)
        
    paginator = Paginator(logs_list, 20)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    
    return render(request, 'audit_logs/verification_logs.html', {
        'logs': logs,
        'query': query,
        'status_filter': status_filter
    })
