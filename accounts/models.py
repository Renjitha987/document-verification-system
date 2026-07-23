from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_student(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    register_number = models.CharField(max_length=50, unique=True, db_index=True)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    department = models.ForeignKey('certificates.Department', on_delete=models.PROTECT, related_name='students')
    course = models.ForeignKey('certificates.Course', on_delete=models.PROTECT, related_name='students')
    college_name = models.CharField(max_length=200)
    university_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.register_number}"
