from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Course, QRCode, Attendance, CustomUser
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

@login_required
def generate_qr_code(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    # Optional: Add a check to ensure the user is the teacher for this course
    if request.user.role != 'Teacher' or request.user != course.teacher:
        return HttpResponseForbidden("You are not authorized to generate a QR code for this course.")

    expires_at = timezone.now() + timedelta(minutes=5)
    qr_code = QRCode.objects.create(course=course, expires_at=expires_at)
    
    context = {
        'course': course,
        'qr_code_data': str(qr_code.qr_code_data),
    }
    return render(request, 'generate_qr.html', context)

@login_required
@require_POST
def mark_attendance(request):
    try:
        data = json.loads(request.body)
        qr_code_data = data.get('qr_code_data')

        if not qr_code_data:
            return JsonResponse({'success': False, 'message': 'QR code data not provided.'})

        try:
            qr_code = QRCode.objects.get(qr_code_data=qr_code_data)
        except QRCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid QR code.'})

        if timezone.now() > qr_code.expires_at:
            return JsonResponse({'success': False, 'message': 'QR code has expired.'})

        student = request.user
        if student.role != 'Student':
            return JsonResponse({'success': False, 'message': 'Only students can mark attendance.'})

        course = qr_code.course
        lecture_date = timezone.now().date()

        if Attendance.objects.filter(student=student, course=course, lecture_date=lecture_date).exists():
            return JsonResponse({'success': False, 'message': 'Attendance already marked for this lecture.'})

        Attendance.objects.create(student=student, course=course, lecture_date=lecture_date, is_present=True)
        return JsonResponse({'success': True, 'message': 'Attendance marked successfully.'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'Teacher':
            return redirect('teacher_dashboard')
        elif request.user.role == 'Student':
            return redirect('student_dashboard')
        else:
            return redirect('/admin/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'Teacher':
                return redirect('teacher_dashboard')
            elif user.role == 'Student':
                return redirect('student_dashboard')
            else:
                return redirect('/admin/')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')

@login_required
def teacher_dashboard(request):
    if request.user.role != 'Teacher':
        return HttpResponseForbidden("You are not authorized to view this page.")
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'core/teacher_dashboard.html', {'courses': courses})

@login_required
def view_report(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.role != 'Teacher' or request.user != course.teacher:
        return HttpResponseForbidden("You are not authorized to view this report.")
    # Placeholder for report generation logic
    return render(request, 'core/view_report.html', {'course': course})

@login_required
def student_dashboard(request):
    if request.user.role != 'Student':
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    enrolled_courses = request.user.enrolled_courses.all()
    enrollments = []
    for course in enrolled_courses:
        total_lectures = Attendance.objects.filter(course=course).values('lecture_date').distinct().count()
        attended_lectures = Attendance.objects.filter(course=course, student=request.user, is_present=True).count()
        attendance_percentage = (attended_lectures / total_lectures) * 100 if total_lectures > 0 else 0
        enrollments.append({
            'course': course,
            'attendance_percentage': round(attendance_percentage)
        })
    
    return render(request, 'core/student_dashboard.html', {'enrollments': enrollments})

@login_required
def scan_qr_code(request):
    return render(request, 'core/scan_qr.html')

@login_required
def profile(request):
    return render(request, 'core/profile.html')

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')
