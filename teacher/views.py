from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Course, Class, QRCode, Attendance, Lecture, Subject
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
    
    subjects = Subject.objects.filter(teacher=request.user).select_related('class_obj__course')
    
    courses_data = {}
    for subject in subjects:
        course = subject.class_obj.course
        if course not in courses_data:
            courses_data[course] = {}
        
        class_obj = subject.class_obj
        if class_obj not in courses_data[course]:
            courses_data[course][class_obj] = []
            
        courses_data[course][class_obj].append(subject)

    context = {
        'courses_data': courses_data,
    }
    return render(request, 'teacher/teacher_dashboard.html', context)

@login_required
def select_class_view(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied

    courses = Course.objects.prefetch_related('classes').all()
    
    context = {
        'courses': courses,
    }
    return render(request, 'teacher/select_class.html', context)

@login_required
def create_subject_view(request, class_id):
    if request.user.role != 'Teacher':
        raise PermissionDenied
        
    class_obj = get_object_or_404(Class, pk=class_id)
    
    if request.method == 'POST':
        subject_name = request.POST.get('name')
        if subject_name:
            Subject.objects.create(name=subject_name, class_obj=class_obj, teacher=request.user)
            messages.success(request, f'Subject "{subject_name}" created for {class_obj.name}.')
            return redirect('teacher:teacher_dashboard')
        else:
            messages.error(request, 'Subject name cannot be empty.')
            
    context = {
        'class_obj': class_obj,
    }
    return render(request, 'teacher/create_subject.html', context)

@login_required
def generate_qr_code(request, lecture_id):
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    
    # This check needs to be updated since teacher is not directly on class_obj
    # We can check if the teacher teaches any subject in this class
    subjects_in_class = Subject.objects.filter(class_obj=lecture.class_obj, teacher=request.user)
    if request.user.role != 'Teacher' or not subjects_in_class.exists():
        return HttpResponseForbidden("You are not authorized to generate a QR code for this lecture.")

    # Check for an existing active QR code for this lecture
    active_qr_code = QRCode.objects.filter(
        lecture=lecture,
        expires_at__gt=timezone.now()
    ).first()

    if active_qr_code:
        qr_code = active_qr_code
    else:
        # If no active QR code, create a new one
        expires_at = timezone.now() + timedelta(minutes=2)
        qr_code = QRCode.objects.create(lecture=lecture, expires_at=expires_at)
    
    context = {
        'lecture': lecture,
        'qr_code_data': str(qr_code.qr_code_data),
        'expires_at': qr_code.expires_at.isoformat(),
    }
    return render(request, 'teacher/generate_qr.html', context)

@login_required
def view_report(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id)
    # This check needs to be updated
    subjects_in_class = Subject.objects.filter(class_obj=class_obj, teacher=request.user)
    if request.user.role != 'Teacher' or not subjects_in_class.exists():
        return HttpResponseForbidden("You are not authorized to view this report for this class.")

    students = class_obj.students.all()
    total_students = students.count()
    total_lectures = Lecture.objects.filter(class_obj=class_obj).count()

    student_reports = []
    total_attendance_sum = 0

    for student in students:
        attended_lectures = Attendance.objects.filter(lecture__class_obj=class_obj, student=student).count()
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
def schedule_lecture_view(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id)
    # This check needs to be updated
    subjects_in_class = Subject.objects.filter(class_obj=class_obj, teacher=request.user)
    if request.user.role != 'Teacher' or not subjects_in_class.exists():
        raise PermissionDenied

    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        if date and time:
            Lecture.objects.create(class_obj=class_obj, date=date, time=time)
            messages.success(request, f'Lecture scheduled successfully for {class_obj.name}.')
            return redirect('teacher:teacher_dashboard') # Or maybe to a lecture list view
        else:
            messages.error(request, 'Date and time cannot be empty.')

    context = {
        'class_obj': class_obj
    }
    return render(request, 'teacher/schedule_lecture.html', context)


@login_required
def view_lectures(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id)
    # This check needs to be updated
    subjects_in_class = Subject.objects.filter(class_obj=class_obj, teacher=request.user)
    if request.user.role != 'Teacher' or not subjects_in_class.exists():
        raise PermissionDenied
    
    lectures = Lecture.objects.filter(class_obj=class_obj).order_by('-date', '-time')
    
    context = {
        'class_obj': class_obj,
        'lectures': lectures
    }
    return render(request, 'teacher/view_lectures.html', context)


@login_required
@require_POST # Ensure this view is only accessed via POST
def prune_lectures_view(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied

    try:
        days_to_keep = int(request.POST.get('days', 1825))
    except (ValueError, TypeError):
        messages.error(request, 'Invalid number of days provided.')
        return redirect(request.META.get('HTTP_REFERER', 'teacher:teacher_dashboard'))

    cutoff_date = timezone.now() - timedelta(days=days_to_keep)

    # We should only prune lectures for the classes taught by the current teacher
    # to prevent one teacher from deleting another's data.
    # This logic needs to be updated
    old_lectures = Lecture.objects.filter(
        class_obj__subjects__teacher=request.user,
        date__lt=cutoff_date
    ).distinct()
    
    count = old_lectures.count()

    if count == 0:
        messages.info(request, 'No old lectures found to delete.')
    else:
        old_lectures.delete()
        messages.success(request, f'Successfully deleted {count} old lecture record(s).')

    # Redirect back to the page the user came from.
    return redirect(request.META.get('HTTP_REFERER', 'teacher:teacher_dashboard'))

@login_required
def get_attendance_data(request, class_id):
    # 1. Validate user and class
    # This check needs to be updated
    class_obj = get_object_or_404(Class, pk=class_id)
    subjects_in_class = Subject.objects.filter(class_obj=class_obj, teacher=request.user)
    if request.user.role != 'Teacher' or not subjects_in_class.exists():
        return JsonResponse({'error': 'Class not found or you do not have permission to view it.'}, status=404)

    # 2. Get all lectures for the class
    lectures = Lecture.objects.filter(class_obj=class_obj).order_by('date', 'time')

    # 3. Get total number of students in the class
    total_students = class_obj.students.count()

    # 4. Calculate attendance percentage for each lecture
    attendance_data = []
    for lecture in lectures:
        present_students = Attendance.objects.filter(lecture=lecture).count()
        if total_students > 0:
            percentage = (present_students / total_students) * 100
        else:
            percentage = 0
        attendance_data.append({
            'date': lecture.date.strftime('%Y-%m-%d'),
            'percentage': round(percentage, 2)
        })

    # 5. Return data as JSON
    return JsonResponse(attendance_data, safe=False)

@login_required
def reports_view(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied
    
    # This needs to be updated
    subjects = Subject.objects.filter(teacher=request.user).select_related('class_obj__course')
    
    courses_data = {}
    for subject in subjects:
        course = subject.class_obj.course
        if course not in courses_data:
            courses_data[course] = []
        
        # Avoid adding duplicate classes
        if not any(d.id == subject.class_obj.id for d in courses_data[course]):
             courses_data[course].append(subject.class_obj)

    context = {
        'courses_with_classes': courses_data,
    }
    return render(request, 'teacher/reports.html', context)
