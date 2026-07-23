from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from certificates.models import Certificate, Department, Course
from audit_logs.models import AuditLog
from audit_logs.utils import log_action
from django.shortcuts import get_object_or_404
from .models import StudentProfile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_router(request):
    """Routes users to their respective dashboards based on their role."""
    if request.user.is_admin():
        return redirect('admin_dashboard')
    elif request.user.is_student():
        return redirect('student_dashboard')
    else:
        messages.error(request, "Access denied. Role not configured.")
        return redirect('home')


@login_required
def student_dashboard(request):
    if not request.user.is_student():
        return redirect('admin_dashboard')
        
    # Get student profile
    profile = getattr(request.user, 'student_profile', None)
    if not profile:
        messages.error(request, "Student profile not found. Please contact the administrator.")
        logout(request)
        return redirect('login')
        
    certificates = Certificate.objects.filter(student=profile).order_by('-issue_date')
    verified_count = certificates.filter(status='APPROVED').count()
    pending_count = certificates.filter(status='PENDING').count()
    
    # Recent logs for this student
    recent_logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    context = {
        'profile': profile,
        'certificates': certificates,
        'verified_count': verified_count,
        'pending_count': pending_count,
        'total_count': certificates.count(),
        'recent_logs': recent_logs,
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def student_certificates(request):
    if not request.user.is_student():
        return redirect('admin_dashboard')
        
    profile = request.user.student_profile
    certificates = Certificate.objects.filter(student=profile).order_by('-issue_date')
    
    return render(request, 'accounts/student_certificates.html', {'certificates': certificates})


@login_required
@transaction.atomic
def student_profile(request):
    if not request.user.is_student():
        return redirect('admin_dashboard')
        
    profile = request.user.student_profile
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        father_name = request.POST.get('father_name', '').strip()
        mother_name = request.POST.get('mother_name', '').strip()
        
        # Simple validations
        if not first_name or not email:
            messages.error(request, "First Name and Email are required.")
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            profile.father_name = father_name
            profile.mother_name = mother_name
            profile.save()
            
            log_action(user, 'UPDATE_PROFILE', "Student updated their profile details.", request)
            messages.success(request, "Profile updated successfully!")
            return redirect('student_profile')
            
    return render(request, 'accounts/student_profile.html', {'profile': profile, 'user': user})


@transaction.atomic
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    User = get_user_model()
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        register_number = request.POST.get('register_number', '').strip()
        father_name = request.POST.get('father_name', '').strip()
        mother_name = request.POST.get('mother_name', '').strip()
        department_id = request.POST.get('department', '')
        course_id = request.POST.get('course', '')
        college_name = request.POST.get('college_name', '').strip()
        university_name = request.POST.get('university_name', '').strip()
        
        # Validations
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif StudentProfile.objects.filter(register_number=register_number).exists():
            messages.error(request, "Register Number already registered.")
        else:
            try:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role='student'
                )
                
                # Fetch FKs
                dept = Department.objects.get(id=department_id)
                course = Course.objects.get(id=course_id)
                
                # Create Student Profile
                profile = StudentProfile.objects.create(
                    user=user,
                    register_number=register_number,
                    father_name=father_name,
                    mother_name=mother_name,
                    department=dept,
                    course=course,
                    college_name=college_name,
                    university_name=university_name
                )
                
                log_action(user, 'REGISTER', f"New student registered with username {username} and register number {register_number}.", request)
                login(request, user)  # Auto login after successful registration
                messages.success(request, f"Registration successful! Welcome to the portal, {first_name}!")
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f"Registration failed. Error: {str(e)}")
                
    departments = Department.objects.all()
    courses = Course.objects.all()
    return render(request, 'accounts/register.html', {
        'departments': departments,
        'courses': courses
    })
