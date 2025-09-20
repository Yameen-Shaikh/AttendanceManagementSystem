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
    
    classes_taught = Class.objects.filter(teacher=request.user).order_by('course__name', 'name')

    courses_with_classes = {}
    for class_obj in classes_taught:
        if class_obj.course not in courses_with_classes:
            courses_with_classes[class_obj.course] = []
        courses_with_classes[class_obj.course].append(class_obj)

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
            Course.objects.create(name=course_name)
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
        if class_name:
            if Class.objects.filter(course=course, name=class_name).exists():
                messages.error(request, f'A class named "{class_name}" already exists for this course.')
            else:
                Class.objects.create(name=class_name, course=course, teacher=request.user)
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

    expires_at = timezone.now() + timedelta(minutes=5)
    qr_code = QRCode.objects.create(class_field=class_obj, expires_at=expires_at)
    
    context = {
        'course': class_obj.course,
        'class_obj': class_obj,
        'qr_code_data': str(qr_code.qr_code_data),
        'subjects': class_obj.teacher.subjects,
        'expires_at': expires_at.isoformat(),
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
        subjects = request.POST.get('subjects', '')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'teacher/register.html')

        user = CustomUser.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            role='Teacher',
            is_active=False, # Teachers need approval
            subjects=subjects
        )
        
        messages.success(request, 'Registration successful. Your account is pending approval from an administrator.')
        return redirect('login')

    return render(request, 'teacher/register.html')