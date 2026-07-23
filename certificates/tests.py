import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import StudentProfile
from certificates.models import Department, Course, Certificate

User = get_user_model()

class CertificateVerificationTestCase(TestCase):
    def setUp(self):
        # Create administrative user
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.org',
            password='password123',
            role='admin'
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='teststudent',
            email='student@test.org',
            password='password123',
            role='student'
        )
        
        # Create Department
        self.dept = Department.objects.create(
            name='Computer Science',
            code='CSE'
        )
        
        # Create Course
        self.course = Course.objects.create(
            name='B.Tech CSE',
            code='BTECH-CSE',
            department=self.dept
        )
        
        # Create StudentProfile
        self.profile = StudentProfile.objects.create(
            user=self.student_user,
            register_number='REG-TEST-01',
            father_name='Father Doe',
            mother_name='Mother Doe',
            department=self.dept,
            course=self.course,
            college_name='Test College',
            university_name='Test University'
        )
        
        # Create Certificate
        self.cert = Certificate.objects.create(
            student=self.profile,
            department=self.dept,
            course=self.course,
            semester='Semester 8',
            cgpa=9.50,
            grade='A+',
            issue_date=datetime.date(2026, 5, 10),
            status='APPROVED'
        )
        
        self.client = Client()

    def test_certificate_auto_generation(self):
        """Verify that signature hash and QR code are automatically populated on save."""
        self.assertIsNotNone(self.cert.certificate_number)
        self.assertTrue(self.cert.certificate_number.startswith('CERT-'))
        self.assertEqual(self.cert.student_name_snapshot, self.student_user.get_full_name() or self.student_user.username)
        self.assertIsNotNone(self.cert.digital_signature)
        self.assertEqual(len(self.cert.digital_signature), 64) # SHA-256 length
        self.assertIsNotNone(self.cert.qr_code_image)

    def test_public_verification_view_success(self):
        """Test verification search page returns details for valid credentials."""
        url = reverse('verify')
        response = self.client.get(url, {
            'certificate_number': self.cert.certificate_number,
            'register_number': self.profile.register_number
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Certificate Verified')
        self.assertContains(response, self.cert.student_name_snapshot)

    def test_public_verification_view_failure(self):
        """Test verification search page returns error when invalid credentials are searched."""
        url = reverse('verify')
        response = self.client.get(url, {
            'certificate_number': 'CERT-INVALID-NUM',
            'register_number': 'REG-INVALID-NUM'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Certificate Not Found')

    def test_verification_api_success(self):
        """Test REST API endpoint returns JSON data for valid credentials."""
        url = reverse('verify_certificate_api')
        response = self.client.get(url, {
            'certificate_number': self.cert.certificate_number,
            'register_number': self.profile.register_number
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'verified')
        self.assertEqual(data['certificate']['student_name'], self.cert.student_name_snapshot)
        self.assertEqual(data['certificate']['digital_signature'], self.cert.digital_signature)

    def test_verification_api_failure(self):
        """Test REST API returns 404 error code for invalid credentials."""
        url = reverse('verify_certificate_api')
        response = self.client.get(url, {
            'certificate_number': 'INVALID',
            'register_number': 'INVALID'
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['status'], 'not_found')

    def test_student_registration_success(self):
        """Test student register form successfully provisions account and profile."""
        url = reverse('register')
        response = self.client.post(url, {
            'username': 'newstudent',
            'email': 'new@student.edu',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'Student',
            'register_number': 'REG-NEW-99',
            'father_name': 'Father New',
            'mother_name': 'Mother New',
            'department': self.dept.id,
            'course': self.course.id,
            'college_name': 'New College',
            'university_name': 'New University'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertTrue(StudentProfile.objects.filter(register_number='REG-NEW-99').exists())
