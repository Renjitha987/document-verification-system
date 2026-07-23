from django import forms
from .models import Department, Course, Certificate
from accounts.models import StudentProfile

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Code (e.g. CSE)'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Course Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Code (e.g. BTECH-CSE)'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            'certificate_number', 'student', 'department', 'course', 
            'semester', 'cgpa', 'grade', 'issue_date', 'expiry_date', 
            'pdf_file', 'status'
        ]
        widgets = {
            'certificate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to auto-generate'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Semester 8'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 9.20'}),
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A+'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
