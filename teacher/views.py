from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Course, Class, QRCode, Attendance
from student.models import CustomUser
from django.http import JsonResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

@login_required
def teacher_dashboard(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied
    
    courses = Course.objects.filter(teacher=request.user)
    courses_with_classes = {}
    for course in courses:
        classes = Class.objects.filter(course=course)
        courses_with_classes[course] = list(classes)

    context = {
        'courses_with_classes': courses_with_classes,
        'subjects': request.user.subjects
    }
    return render(request, 'teacher/teacher_dashboard.html', context)

@login_required
def create_course_view(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied

    if request.method == 'POST':
        course_name = request.POST.get('name')
        if course_name:
            Course.objects.create(name=course_name, teacher=request.user)
            messages.success(request, f'Course "{course_name}" created successfully.')
            return redirect('teacher:teacher_dashboard')
        else:
            messages.error(request, 'Course name cannot be empty.')
    
    return render(request, 'teacher/create_course.html')

@login_required
def create_class_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.user.role != 'Teacher':
        return HttpResponseForbidden("You are not authorized to create a class.")

    if request.method == 'POST':
        class_name = request.POST.get('name')
        subject = request.POST.get('subject') # Get subject from form
        if class_name:
            if Class.objects.filter(course=course, name=class_name).exists():
                messages.error(request, f'A class named "{class_name}" already exists for this course.')
            else:
                Class.objects.create(name=class_name, course=course, teacher=request.user, subject=subject) # Save subject
                messages.success(request, f'Class "{class_name}" created successfully for {course.name}.')
                return redirect('teacher:teacher_dashboard')
        else:
            messages.error(request, 'Class name cannot be empty.')
    
    context = {
        'course': course
    }
    return render(request, 'teacher/create_class.html', context)

@login_required
def generate_qr_code(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id)
    
    if request.user.role != 'Teacher' or request.user != class_obj.teacher:
        return HttpResponseForbidden("You are not authorized to generate a QR code for this class.")

    # Check for an existing active QR code for this class
    # Filter by class_field and check if expires_at is in the future
    active_qr_code = QRCode.objects.filter(
        class_field=class_obj,
        expires_at__gt=timezone.now()
    ).first()

    if active_qr_code:
        qr_code = active_qr_code
    else:
        # If no active QR code, create a new one
        expires_at = timezone.now() + timedelta(minutes=2) # Changed to 2 minutes
        qr_code = QRCode.objects.create(class_field=class_obj, expires_at=expires_at)
    
    context = {
        'course': class_obj.course,
        'class_obj': class_obj,
        'qr_code_data': str(qr_code.qr_code_data),
        'expires_at': qr_code.expires_at.isoformat(), # Use the actual expires_at from the QR code object
        'class_name': class_obj.name,
        'subject': class_obj.subject,
    }
    return render(request, 'teacher/generate_qr.html', context)

@login_required
def view_report(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id)
    if request.user.role != 'Teacher' or request.user != class_obj.teacher:
        return HttpResponseForbidden("You are not authorized to view this report for this class.")

    students = class_obj.students.all()
    total_students = students.count()
    total_lectures = Attendance.objects.filter(class_field=class_obj).values('lecture_date').distinct().count()

    student_reports = []
    total_attendance_sum = 0

    for student in students:
        attended_lectures = Attendance.objects.filter(class_field=class_obj, student=student, is_present=True).count()
        attendance_percentage = (attended_lectures / total_lectures) * 100 if total_lectures > 0 else 0
        total_attendance_sum += attendance_percentage
        student_reports.append({
            'student_name': student.name,
            'total_attended': attended_lectures,
            'total_missed': total_lectures - attended_lectures,
            'attendance_percentage': round(attendance_percentage)
        })

    average_attendance = round(total_attendance_sum / total_students) if total_students > 0 else 0

    context = {
        'course': class_obj.course,
        'class_obj': class_obj,
        'total_students': total_students,
        'average_attendance': average_attendance,
        'student_reports': student_reports,
    }
    return render(request, 'teacher/view_report.html', context)

def teacher_register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'teacher/register.html')

        user = CustomUser.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            role='Teacher',
            is_active=False, # Teachers need approval
        )
        
        messages.success(request, 'Registration successful. Your account is pending approval from an administrator.')
        return redirect('login')

    return render(request, 'teacher/register.html')

@login_required
def profile(request):
    return render(request, 'teacher/profile.html')

@login_required
def update_course_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id, teacher=request.user)
    if request.user.role != 'Teacher':
        raise PermissionDenied

    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.save()
        messages.success(request, 'Course updated successfully.')
        return redirect('teacher:teacher_dashboard')
    
    context = {
        'course': course
    }
    return render(request, 'teacher/update_course.html', context)

@login_required
@require_POST
def delete_course_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id, teacher=request.user)
    if request.user.role != 'Teacher':
        raise PermissionDenied
    
    course.delete()
    messages.success(request, 'Course deleted successfully.')
    return redirect('teacher:teacher_dashboard')

@login_required
def update_class_view(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id, teacher=request.user)
    if request.user.role != 'Teacher':
        raise PermissionDenied

    if request.method == 'POST':
        class_obj.name = request.POST.get('name')
        class_obj.subject = request.POST.get('subject')
        class_obj.save()
        messages.success(request, 'Class updated successfully.')
        return redirect('teacher:teacher_dashboard')
    
    context = {
        'class_obj': class_obj
    }
    return render(request, 'teacher/update_class.html', context)

@login_required
@require_POST
def delete_class_view(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id, teacher=request.user)
    if request.user.role != 'Teacher':
        raise PermissionDenied
    
    class_obj.delete()
    messages.success(request, 'Class deleted successfully.')
    return redirect('teacher:teacher_dashboard')

@login_required
def get_attendance_data(request, class_id):
    # 1. Validate user and class
    try:
        class_obj = Class.objects.get(pk=class_id, teacher=request.user)
    except Class.DoesNotExist:
        return JsonResponse({'error': 'Class not found or you do not have permission to view it.'}, status=404)

    # 2. Get all lecture dates for the class
    lecture_dates = Attendance.objects.filter(class_field=class_obj).values_list('lecture_date', flat=True).distinct().order_by('lecture_date')

    # 3. Get total number of students in the class
    total_students = class_obj.students.count()

    # 4. Calculate attendance percentage for each lecture date
    attendance_data = []
    for date in lecture_dates:
        present_students = Attendance.objects.filter(class_field=class_obj, lecture_date=date, is_present=True).count()
        if total_students > 0:
            percentage = (present_students / total_students) * 100
        else:
            percentage = 0
        attendance_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'percentage': round(percentage, 2)
        })

    # 5. Return data as JSON
    return JsonResponse(attendance_data, safe=False)

@login_required
def reports_view(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied
    
    courses = Course.objects.filter(teacher=request.user)
    courses_with_classes = {}
    for course in courses:
        classes = Class.objects.filter(course=course)
        courses_with_classes[course] = list(classes)

    context = {
        'courses_with_classes': courses_with_classes,
    }
    return render(request, 'teacher/reports.html', context)
