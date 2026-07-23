from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import AuditLog
from .utils import get_client_ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_client_ip(request) if request else None
    AuditLog.objects.create(
        user=user,
        action='LOGIN',
        description=f"User {user.username} logged in successfully.",
        ip_address=ip
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ip = get_client_ip(request) if request else None
    if user:
        AuditLog.objects.create(
            user=user,
            action='LOGOUT',
            description=f"User {user.username} logged out.",
            ip_address=ip
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip = get_client_ip(request) if request else None
    username = credentials.get('username', 'Unknown')
    AuditLog.objects.create(
        user=None,
        action='LOGIN_FAILED',
        description=f"Failed login attempt for username: {username}",
        ip_address=ip
    )
