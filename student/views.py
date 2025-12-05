from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CustomUser
from teacher.models import Class, Attendance, QRCode, Lecture, AcademicSession, Subject
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

    try:
        active_session = AcademicSession.objects.get(is_active=True)
    except AcademicSession.DoesNotExist:
        return JsonResponse({'error': 'No active session'}, status=400)

    student = request.user
    enrolled_classes = student.enrolled_classes.filter(session=active_session)
    lectures = Lecture.objects.filter(
        subject__class_obj__in=enrolled_classes,
        date__range=[start_date, end_date]
    )

    attended_lectures = Attendance.objects.filter(
        student=student,
        lecture__in=lectures,
        status='approved'
    ).values_list('lecture_id', flat=True)

    events = []
    for lecture in lectures:
        is_present = lecture.id in attended_lectures
        events.append({
            'title': 'Present' if is_present else 'Absent',
            'start': lecture.date.isoformat(),
            'allDay': True,
            'color': '#28a745' if is_present else '#dc3545'
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
            qr_code = QRCode.objects.select_related('lecture__subject__class_obj').get(qr_code_data=qr_code_data)
        except QRCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid QR code.'})

        if timezone.now() > qr_code.expires_at:
            return JsonResponse({'success': False, 'message': 'QR code has expired.'})

        student = request.user
        if student.role != 'Student':
            return JsonResponse({'success': False, 'message': 'Only students can mark attendance.'})

        lecture = qr_code.lecture
        if not lecture:
            return JsonResponse({'success': False, 'message': 'This QR code is not linked to a lecture.'})

        subject = lecture.subject
        class_obj = subject.class_obj
        
        if not student.enrolled_classes.filter(pk=class_obj.pk).exists():
            return JsonResponse({'success': False, 'message': f'You are not enrolled in {class_obj.name}.'})

        attendance, created = Attendance.objects.get_or_create(
            student=student,
            lecture=lecture,
            defaults={'subject': subject, 'date': lecture.date, 'status': 'pending'}
        )

        if created:
            # Send real-time notification to the teacher's live attendance page
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"attendance_{lecture.id}",
                {
                    "type": "attendance_update",
                    "data": {
                        "student_name": student.name,
                        "attendance_id": attendance.id,
                        "status": "pending"
                    }
                }
            )
            message = f'Your attendance for {subject.name} has been recorded and is pending approval.'
        else:
            message = f'You have already scanned the code for {subject.name}. Your attendance is pending approval.'

        return JsonResponse({'success': True, 'message': message})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    except Exception as e:
        # Log the error for debugging
        print(f"Error in mark_attendance: {e}")
        return JsonResponse({'success': False, 'message': 'An unexpected error occurred.'})

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
    
    try:
        active_session = AcademicSession.objects.get(is_active=True)
    except AcademicSession.DoesNotExist:
        messages.error(request, "There is no active academic session. Please contact an administrator.")
        return render(request, 'student/student_dashboard.html', {'enrollments': []})

    enrolled_classes = request.user.enrolled_classes.filter(session=active_session)
    enrollments = []
    if enrolled_classes.exists():
        for class_obj in enrolled_classes:
            total_lectures = Lecture.objects.filter(subject__class_obj=class_obj).count()
            attended_lectures = Attendance.objects.filter(lecture__subject__class_obj=class_obj, student=request.user, status='approved').count()
            attendance_percentage = (attended_lectures / total_lectures) * 100 if total_lectures > 0 else 0
            enrollments.append({
                'class_obj': class_obj,
                'attendance_percentage': round(attendance_percentage)
            })
        return render(request, 'student/student_dashboard.html', {'enrollments': enrollments})
    else:
        # Show classes from the active session for enrollment
        classes = Class.objects.filter(session=active_session)
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
            try:
                active_session = AcademicSession.objects.get(is_active=True)
                classes = Class.objects.filter(session=active_session)
            except AcademicSession.DoesNotExist:
                classes = []
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
                active_session = AcademicSession.objects.get(is_active=True)
                class_obj = Class.objects.get(id=class_id, session=active_session)
                class_obj.students.add(user)
                messages.success(request, 'Registration successful. Please login.')
            except (Class.DoesNotExist, AcademicSession.DoesNotExist):
                messages.error(request, 'Invalid class selected for the current session.')
                user.delete()
                try:
                    active_session = AcademicSession.objects.get(is_active=True)
                    classes = Class.objects.filter(session=active_session)
                except AcademicSession.DoesNotExist:
                    classes = []
                return render(request, 'student/register.html', {'classes': classes})
        else:
            messages.success(request, 'Registration successful. Please login.')
        
        return redirect('login')

    try:
        active_session = AcademicSession.objects.get(is_active=True)
        classes = Class.objects.filter(session=active_session)
    except AcademicSession.DoesNotExist:
        messages.error(request, "Registration is currently disabled as there is no active academic session.")
        classes = []
        
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

    student = request.user
    enrolled_classes = student.enrolled_classes.all()
    lectures = Lecture.objects.filter(
        subject__class_obj__in=enrolled_classes,
        date=date
    )

    attended_lectures = Attendance.objects.filter(
        student=student,
        lecture__in=lectures,
        status='approved'
    ).values_list('lecture_id', flat=True)

    data = []
    for lecture in lectures:
        is_present = lecture.id in attended_lectures
        data.append({
            'subject': lecture.subject.name,
            'status': 'Present' if is_present else 'Absent'
        })

    return JsonResponse(data, safe=False)

@login_required
def unenroll(request, class_id):
    try:
        active_session = AcademicSession.objects.get(is_active=True)
        class_obj = get_object_or_404(Class, id=class_id, session=active_session)
    except (AcademicSession.DoesNotExist, Class.DoesNotExist):
        messages.error(request, 'This class is not available in the current academic session.')
        return redirect('student:student_dashboard')

    if request.user in class_obj.students.all():
        class_obj.students.remove(request.user)
        messages.success(request, f'You have been unenrolled from {class_obj.name}.')
    else:
        messages.error(request, f'You are not enrolled in {class_obj.name}.')
    return redirect('student:student_dashboard')

@login_required
def enroll(request, class_id):
    try:
        active_session = AcademicSession.objects.get(is_active=True)
        class_obj = get_object_or_404(Class, id=class_id, session=active_session)
    except (AcademicSession.DoesNotExist, Class.DoesNotExist):
        messages.error(request, 'This class is not available in the current academic session.')
        return redirect('student:student_dashboard')

    if request.user not in class_obj.students.all():
        class_obj.students.add(request.user)
        messages.success(request, f'You have been enrolled in {class_obj.name}.')
    else:
        messages.warning(request, f'You are already enrolled in {class_obj.name}.')
    return redirect('student:student_dashboard')

@login_required
def reports(request):
    try:
        active_session = AcademicSession.objects.get(is_active=True)
    except AcademicSession.DoesNotExist:
        messages.error(request, "Reports are unavailable as there is no active academic session.")
        return render(request, 'student/reports.html', {'subjects': []})

    enrolled_classes = request.user.enrolled_classes.filter(session=active_session)
    subjects = Subject.objects.filter(class_obj__in=enrolled_classes).order_by('class_obj__course__name', 'name')
    
    context = {
        'subjects': subjects
    }
    return render(request, 'student/reports.html', context)


@login_required
def get_student_subject_attendance_data(request):
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Subject ID is required.'}, status=400)

    try:
        subject = Subject.objects.get(pk=subject_id)
        # Permission check: Ensure the student is enrolled in the subject's class
        if not request.user.enrolled_classes.filter(pk=subject.class_obj.pk).exists():
            return JsonResponse({'error': 'Permission denied.'}, status=403)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found.'}, status=404)

    total_lectures = Lecture.objects.filter(subject=subject).count()
    
    if total_lectures == 0:
        return JsonResponse({'attended': 0, 'missed': 0})

    attended_lectures = Attendance.objects.filter(
        student=request.user,
        lecture__subject=subject,
        status='approved'
    ).count()

    return JsonResponse({
        'attended': attended_lectures,
        'missed': total_lectures - attended_lectures
    })

@login_required
def get_student_attendance_trend(request):
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Subject ID is required.'}, status=400)

    try:
        subject = Subject.objects.get(pk=subject_id)
        if not request.user.enrolled_classes.filter(pk=subject.class_obj.pk).exists():
            return JsonResponse({'error': 'Permission denied.'}, status=403)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found.'}, status=404)

    lectures = Lecture.objects.filter(subject=subject).order_by('date')
    if not lectures.exists():
        return JsonResponse({'labels': [], 'data': []})

    attended_lecture_ids = set(Attendance.objects.filter(
        student=request.user,
        lecture__in=lectures,
        status='approved'
    ).values_list('lecture_id', flat=True))

    labels = [lecture.date.strftime('%Y-%m-%d') for lecture in lectures]
    data = [1 if lecture.id in attended_lecture_ids else 0 for lecture in lectures]

    return JsonResponse({'labels': labels, 'data': data})
