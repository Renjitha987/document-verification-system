import uuid
import hashlib
import io
import qrcode
from django.db import models
from django.core.files.base import ContentFile
from accounts.models import StudentProfile

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Certificate(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved / Verified'),
        ('REJECTED', 'Rejected'),
        ('REVOKED', 'Revoked'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_number = models.CharField(max_length=50, unique=True, db_index=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='certificates')
    student_name_snapshot = models.CharField(max_length=150, blank=True, help_text="Snapshot of student name at time of issuance")
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    semester = models.CharField(max_length=20)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    grade = models.CharField(max_length=5)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    
    # Uploaded PDF file
    pdf_file = models.FileField(upload_to='certificates/pdfs/', null=True, blank=True)
    
    # Auto-generated QR code image
    qr_code_image = models.ImageField(upload_to='certificates/qrcodes/', blank=True)
    
    # Cryptographic hash acting as digital signature
    digital_signature = models.CharField(max_length=64, unique=True, blank=True, db_index=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_signature(self):
        """Generates a SHA-256 hash hash of key certificate attributes"""
        data = f"{self.certificate_number}|{self.student.register_number}|{self.student_name_snapshot}|{float(self.cgpa):.2f}|{self.grade}|{self.issue_date}|django-secure-salt-2026"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def generate_qr_code(self):
        """Generates the QR code pointing to the public verification URL"""
        # Verification URL schema matching the router definition
        verify_url = f"/verify/?certificate_number={self.certificate_number}&register_number={self.student.register_number}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=3,
        )
        qr.add_data(verify_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        
        # Save to ImageField
        filename = f"qr_{self.certificate_number}.png"
        self.qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        # Auto-generate a clean certificate number if empty
        if not self.certificate_number:
            self.certificate_number = f"CERT-{self.issue_date.year}-{uuid.uuid4().hex[:8].upper()}"
            
        # Snapshot name for archival history
        if not self.student_name_snapshot and self.student:
            self.student_name_snapshot = self.student.user.get_full_name() or self.student.user.username
            
        # Generate the signature hash
        self.digital_signature = self.generate_signature()
        
        # Generate the QR Code (only generate if not already generated, or if cert number changed)
        # To handle update save cleanly without infinite recursion:
        if not self.qr_code_image:
            self.generate_qr_code()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.certificate_number} - {self.student_name_snapshot}"
