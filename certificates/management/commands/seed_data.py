import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import StudentProfile
from certificates.models import Department, Course, Certificate
from audit_logs.models import AuditLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial departments, courses, students, administrative accounts, and certificates.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database records...')
        
        # 1. Create Admin Account
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@verification-system.org',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('adminpass')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin account created: admin / adminpass'))
        else:
            self.stdout.write('Admin user already exists.')

        # 2. Create Departments
        cse_dept, _ = Department.objects.get_or_create(
            code='CSE',
            defaults={'name': 'Computer Science & Engineering'}
        )
        ece_dept, _ = Department.objects.get_or_create(
            code='ECE',
            defaults={'name': 'Electronics & Communication Engineering'}
        )
        self.stdout.write('Departments created: CSE, ECE')

        # 3. Create Courses
        cse_course, _ = Course.objects.get_or_create(
            code='BTECH-CSE',
            department=cse_dept,
            defaults={'name': 'B.Tech Computer Science & Engineering'}
        )
        ece_course, _ = Course.objects.get_or_create(
            code='BTECH-ECE',
            department=ece_dept,
            defaults={'name': 'B.Tech Electronics & Communication Engineering'}
        )
        self.stdout.write('Courses created: BTECH-CSE, BTECH-ECE')

        # 4. Create Student Users and Profiles
        student_user1, c1 = User.objects.get_or_create(
            username='student',
            defaults={
                'email': 'student@university.edu',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'student'
            }
        )
        if c1:
            student_user1.set_password('studentpass')
            student_user1.save()
            
        profile1, p_c1 = StudentProfile.objects.get_or_create(
            user=student_user1,
            defaults={
                'register_number': 'REG-2026-001',
                'father_name': 'Robert Doe',
                'mother_name': 'Mary Doe',
                'department': cse_dept,
                'course': cse_course,
                'college_name': 'Institute of Technology',
                'university_name': 'State University'
            }
        )
        if p_c1:
            self.stdout.write(self.style.SUCCESS('Student account 1 created: student / studentpass (REG-2026-001)'))
            
        student_user2, c2 = User.objects.get_or_create(
            username='student2',
            defaults={
                'email': 'student2@university.edu',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'student'
            }
        )
        if c2:
            student_user2.set_password('studentpass')
            student_user2.save()
            
        profile2, p_c2 = StudentProfile.objects.get_or_create(
            user=student_user2,
            defaults={
                'register_number': 'REG-2026-002',
                'father_name': 'David Smith',
                'mother_name': 'Sarah Smith',
                'department': ece_dept,
                'course': ece_course,
                'college_name': 'Institute of Engineering',
                'university_name': 'State University'
            }
        )
        if p_c2:
            self.stdout.write(self.style.SUCCESS('Student account 2 created: student2 / studentpass (REG-2026-002)'))

        # 5. Create Certificates
        # Approved Cert for Student 1
        cert1, cr1 = Certificate.objects.get_or_create(
            certificate_number='CERT-2026-A101',
            defaults={
                'student': profile1,
                'department': cse_dept,
                'course': cse_course,
                'semester': 'Semester 8',
                'cgpa': 9.20,
                'grade': 'A+',
                'issue_date': datetime.date(2026, 5, 15),
                'status': 'APPROVED',
                'verification_date': timezone.now()
            }
        )
        if cr1:
            self.stdout.write(self.style.SUCCESS('Created approved certificate CERT-2026-A101'))

        # Approved Cert for Student 2
        cert2, cr2 = Certificate.objects.get_or_create(
            certificate_number='CERT-2026-B202',
            defaults={
                'student': profile2,
                'department': ece_dept,
                'course': ece_course,
                'semester': 'Semester 8',
                'cgpa': 8.75,
                'grade': 'A',
                'issue_date': datetime.date(2026, 5, 15),
                'status': 'APPROVED',
                'verification_date': timezone.now()
            }
        )
        if cr2:
            self.stdout.write(self.style.SUCCESS('Created approved certificate CERT-2026-B202'))

        # Revoked Cert for Student 1
        cert3, cr3 = Certificate.objects.get_or_create(
            certificate_number='CERT-2026-C303',
            defaults={
                'student': profile1,
                'department': cse_dept,
                'course': cse_course,
                'semester': 'Semester 7',
                'cgpa': 7.50,
                'grade': 'B',
                'issue_date': datetime.date(2025, 12, 10),
                'status': 'REVOKED'
            }
        )
        if cr3:
            self.stdout.write(self.style.SUCCESS('Created revoked certificate CERT-2026-C303'))

        # Pending Cert for Student 2
        cert4, cr4 = Certificate.objects.get_or_create(
            certificate_number='CERT-2026-D404',
            defaults={
                'student': profile2,
                'department': ece_dept,
                'course': ece_course,
                'semester': 'Semester 6',
                'cgpa': 9.50,
                'grade': 'O',
                'issue_date': datetime.date(2026, 6, 20),
                'status': 'PENDING'
            }
        )
        if cr4:
            self.stdout.write(self.style.SUCCESS('Created pending certificate CERT-2026-D404'))

        # 6. Seed Audit Logs
        AuditLog.objects.get_or_create(
            action='SEED_DATA',
            defaults={
                'user': admin_user,
                'description': 'Database initial seeding command completed.',
                'ip_address': '127.0.0.1'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
