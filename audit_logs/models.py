from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=50)  # e.g., 'LOGIN', 'CREATE_CERTIFICATE', 'APPROVE_CERTIFICATE'
    description = models.TextField()
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else "System/Anonymous"
        return f"[{self.timestamp}] {user_str} - {self.action}: {self.description[:50]}"


class VerificationHistory(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Verified Successfully'),
        ('FAILED', 'Certificate Not Found / Invalid'),
    )
    searched_certificate_number = models.CharField(max_length=50)
    searched_register_number = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.searched_certificate_number} / {self.searched_register_number} - {self.status}"
