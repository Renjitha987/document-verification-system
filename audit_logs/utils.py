from .models import AuditLog

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(user, action, description, request=None):
    ip = get_client_ip(request) if request else None
    return AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip
    )
