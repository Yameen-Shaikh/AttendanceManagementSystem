from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CustomUser
from teacher.models import Class, Attendance, QRCode
from django.http import JsonResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
import json
import random
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@login_required
def get_attendance_calendar_data(request):
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'Start and end dates are required.'}, status=400)

    try:
        start_date = datetime.fromisoformat(start_date_str.split('T')[0])
        end_date = datetime.fromisoformat(end_date_str.split('T')[0])
    except ValueError:
        return JsonResponse({'error': 'Invalid date format.'}, status=400)

    attendances = Attendance.objects.filter(
        student=request.user,
        lecture_date__range=[start_date, end_date]
    )

    events = []
    for attendance in attendances:
        events.append({
            'title': 'Present' if attendance.is_present else 'Absent',
            'start': attendance.lecture_date.isoformat(),
            'allDay': True,
            'color': '#28a745' if attendance.is_present else '#dc3545'
        })

    return JsonResponse(events, safe=False)

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

        class_obj = qr_code.class_field
        
        # Check if the student is enrolled in the class
        if student not in class_obj.students.all():
            return JsonResponse({'success': False, 'message': 'You are not enrolled in this class.'})

        lecture_date = timezone.now().date()

        if Attendance.objects.filter(student=student, class_field=class_obj, lecture_date=lecture_date).exists():
            return JsonResponse({'success': False, 'message': 'Attendance already marked for this lecture.'})

        Attendance.objects.create(student=student, class_field=class_obj, lecture_date=lecture_date, is_present=True)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{class_obj.id}',
            {
                'type': 'send_notification',
                'message': 'Attendance marked successfully.'
            }
        )

        return JsonResponse({'success': True, 'message': f'Attendance marked successfully for {class_obj.subject}.'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'Teacher':
            return redirect('teacher:teacher_dashboard')
        elif request.user.role == 'Student':
            return redirect('student:student_dashboard')
        else:
            return redirect('/admin/')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.role == 'Teacher' and not user.is_approved:
                messages.error(request, 'Invalid email or password/Approval pending')
                return redirect('login')
            login(request, user)
            if user.role == 'Teacher':
                return redirect('teacher:teacher_dashboard')
            elif user.role == 'Student':
                return redirect('student:student_dashboard')
            else:
                return redirect('/admin/')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def student_dashboard(request):
    if request.user.role != 'Student':
        raise PermissionDenied
    
    enrolled_classes = request.user.enrolled_classes.all()
    enrollments = []
    if enrolled_classes.exists():
        for class_obj in enrolled_classes:
            total_lectures = Attendance.objects.filter(class_field=class_obj).values('lecture_date').distinct().count()
            attended_lectures = Attendance.objects.filter(class_field=class_obj, student=request.user, is_present=True).count()
            attendance_percentage = (attended_lectures / total_lectures) * 100 if total_lectures > 0 else 0
            enrollments.append({
                'class_obj': class_obj,
                'attendance_percentage': round(attendance_percentage)
            })
        return render(request, 'student/student_dashboard.html', {'enrollments': enrollments})
    else:
        classes = Class.objects.all()
        return render(request, 'student/student_dashboard.html', {'classes': classes})

@login_required
def scan_qr_code(request):
    return render(request, 'student/scan_qr.html')

@login_required
def profile(request):
    return render(request, 'student/profile.html')



def student_register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        class_id = request.POST.get('class_id')
        roll_no = request.POST.get('roll_no')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            classes = Class.objects.all()
            return render(request, 'student/register.html', {'classes': classes})

        user = CustomUser.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            role='Student',
            is_active=True,
            roll_no=roll_no
        )
        
        if class_id:
            try:
                class_obj = Class.objects.get(id=class_id)
                class_obj.students.add(user)
                messages.success(request, 'Registration successful. Please login.')
            except Class.DoesNotExist:
                messages.error(request, 'Invalid class selected.')
                user.delete()
                classes = Class.objects.all()
                return render(request, 'student/register.html', {'classes': classes})
        else:
            messages.success(request, 'Registration successful. Please login.')
        
        return redirect('login')

    classes = Class.objects.all()
    context = {
        'classes': classes
    }
    return render(request, 'student/register.html', context)

@login_required
def get_attendance_by_date(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date not provided.'}, status=400)

    try:
        date = datetime.fromisoformat(date_str).date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format.'}, status=400)

    attendances = Attendance.objects.filter(student=request.user, lecture_date=date)
    data = []
    for attendance in attendances:
        data.append({
            'subject': attendance.class_field.subject,
            'status': 'Present' if attendance.is_present else 'Absent'
        })

    return JsonResponse(data, safe=False)

@login_required
def unenroll(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if request.user in class_obj.students.all():
        class_obj.students.remove(request.user)
        messages.success(request, f'You have been unenrolled from {class_obj.name}.')
    else:
        messages.error(request, f'You are not enrolled in {class_obj.name}.')
    return redirect('student:student_dashboard')

@login_required
def enroll(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if request.user not in class_obj.students.all():
        class_obj.students.add(request.user)
        messages.success(request, f'You have been enrolled in {class_obj.name}.')
    else:
        messages.warning(request, f'You are already enrolled in {class_obj.name}.')
    return redirect('student:student_dashboard')

@login_required
def reports(request):
    return render(request, 'student/reports.html')

@login_required
def get_attendance_data(request):
    enrolled_classes = request.user.enrolled_classes.all()
    datasets = []
    labels = []
    for class_obj in enrolled_classes:
        attendance_records = Attendance.objects.filter(class_field=class_obj, student=request.user).order_by('lecture_date')
        if not labels:
            labels = [record.lecture_date.strftime('%Y-%m-%d') for record in attendance_records]
        datasets.append({
            'label': class_obj.subject,
            'data': [1 if record.is_present else 0 for record in attendance_records],
            'borderColor': '#%06x' % random.randint(0, 0xFFFFFF),
            'fill': False
        })
    return JsonResponse({'labels': labels, 'datasets': datasets})
