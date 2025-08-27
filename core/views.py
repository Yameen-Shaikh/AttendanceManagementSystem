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

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = CustomUser.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/dashboard/') # Redirect to a success page.
            else:
                messages.error(request, 'Invalid email or password.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'core/login.html')