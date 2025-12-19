import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Course, Class, QRCode, Attendance, Lecture, Subject, AcademicSession
from student.models import CustomUser
from django.http import JsonResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db.models import Prefetch, Q
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@login_required
def teacher_dashboard(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied
    
    try:
        active_session = AcademicSession.objects.get(is_active=True)
    except AcademicSession.DoesNotExist:
        # Handle case where no active session is set
        messages.error(request, "There is no active academic session. Please contact an administrator.")
        return render(request, 'teacher/teacher_dashboard.html', {'courses_data': {}})

    subjects = Subject.objects.filter(
        teacher=request.user,
        class_obj__session=active_session
    ).select_related('class_obj__course')
    
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

    try:
        active_session = AcademicSession.objects.get(is_active=True)
    except AcademicSession.DoesNotExist:
        messages.error(request, "There is no active academic session. Please contact an administrator.")
        return render(request, 'teacher/select_class.html', {'courses': []})

    courses = Course.objects.prefetch_related(
        Prefetch(
            'classes',
            queryset=Class.objects.filter(session=active_session),
            to_attr='active_classes'
        )
    ).all()
    
    courses_with_active_classes = [course for course in courses if hasattr(course, 'active_classes') and course.active_classes]

    context = {
        'courses': courses_with_active_classes,
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
    
    # Permission check: ensure the teacher teaches the subject associated with this lecture
    if request.user.role != 'Teacher' or lecture.subject.teacher != request.user:
        return HttpResponseForbidden("You are not authorized to generate a QR code for this lecture.")

    # Check if the lecture is in the past
    if lecture.date < timezone.now().date():
        messages.error(request, "You cannot generate a QR code for a past lecture.")
        return redirect('teacher:view_lectures', subject_id=lecture.subject.id)

    # Check for an existing active QR code for this lecture
    active_qr_code = QRCode.objects.filter(
        lecture=lecture,
        expires_at__gt=timezone.now()
    ).first()

    if active_qr_code:
        qr_code = active_qr_code
    else:
        # If no active QR code, create a new one
        expires_at = timezone.now() + timedelta(minutes=1)
        # Explicitly generate a UUID for qr_code_data
        new_qr_code_data = str(uuid.uuid4()) 
        qr_code = QRCode.objects.create(
            lecture=lecture, 
            qr_code_data=new_qr_code_data, # Assign the generated UUID
            expires_at=expires_at
        )
    
    pending_attendances = Attendance.objects.filter(
        lecture=lecture,
        status='pending'
    ).select_related('student')

    context = {
        'lecture': lecture,
        'qr_code_data': str(qr_code.qr_code_data),
        'expires_at': qr_code.expires_at.isoformat(),
        'pending_students': pending_attendances,
    }
    return render(request, 'teacher/generate_qr.html', context)

@login_required
def view_report(request, subject_id): # Changed from class_id
    subject = get_object_or_404(Subject, pk=subject_id)
    
    # Permission check: ensure the teacher teaches this subject
    if request.user.role != 'Teacher' or subject.teacher != request.user:
        return HttpResponseForbidden("You are not authorized to view this report for this subject.")

    students = subject.class_obj.students.all() # Students enrolled in the class of the subject
    total_students = students.count()
    total_lectures = Lecture.objects.filter(subject=subject).count() # Filter by subject

    student_reports = []
    total_attendance_sum = 0

    for student in students:
        attended_lectures = Attendance.objects.filter(lecture__subject=subject, student=student, status='approved').count() # Filter by subject
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
        'course': subject.class_obj.course, # Use subject's class's course
        'class_obj': subject.class_obj, # Use subject's class
        'subject': subject, # Pass subject to template
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
        course_id = request.POST.get('course')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            courses = Course.objects.all()
            return render(request, 'teacher/register.html', {'courses': courses})

        course = get_object_or_404(Course, pk=course_id)

        user = CustomUser.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            role='Teacher',
            is_active=False, # Teachers need approval
            course=course
        )
        
        messages.success(request, 'Registration successful. Your account is pending approval from an administrator.')
        return redirect('login')

    courses = Course.objects.all()
    return render(request, 'teacher/register.html', {'courses': courses})

@login_required
def profile(request):
    return render(request, 'teacher/profile.html')

@login_required
def schedule_lecture_view(request, subject_id): # Changed from class_id
    subject = get_object_or_404(Subject, pk=subject_id) # Get Subject object
    
    # Permission check: ensure the teacher teaches this subject
    if request.user.role != 'Teacher' or subject.teacher != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        if date and time:
            Lecture.objects.create(subject=subject, date=date, time=time) # Use subject
            messages.success(request, f'Lecture scheduled successfully for {subject.name} in {subject.class_obj.name}.')
            return redirect('teacher:teacher_dashboard') # Or maybe to a lecture list view
        else:
            messages.error(request, 'Date and time cannot be empty.')

    context = {
        'subject': subject # Pass subject to template
    }
    return render(request, 'teacher/schedule_lecture.html', context)


@login_required
def view_lectures(request, subject_id): # Changed from class_id
    subject = get_object_or_404(Subject, pk=subject_id) # Get Subject object
    
    # Permission check: ensure the teacher teaches this subject
    if request.user.role != 'Teacher' or subject.teacher != request.user:
        raise PermissionDenied
    
    # Show only active (non-archived) lectures
    lectures = Lecture.objects.filter(subject=subject, is_archived=False).order_by('-date', '-time')
    
    context = {
        'subject': subject, # Pass subject to template
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

    # Archive old lectures instead of deleting
    lectures_to_archive = Lecture.objects.filter(
        subject__teacher=request.user,
        date__lt=cutoff_date,
        is_archived=False # Only archive ones that aren't already archived
    )
    
    count = lectures_to_archive.count()

    if count == 0:
        messages.info(request, 'No old lectures found to archive.')
    else:
        lectures_to_archive.update(is_archived=True)
        messages.success(request, f'Successfully archived {count} old lecture record(s).')

    # Redirect back to the page the user came from.
    return redirect(request.META.get('HTTP_REFERER', 'teacher:teacher_dashboard'))


@login_required
def get_teacher_subject_attendance_data(request):
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Subject ID is required.'}, status=400)

    try:
        subject = Subject.objects.get(pk=subject_id)
        # Optional: Add permission check if a teacher should only access their own subjects
        if request.user.role == 'Teacher' and subject.teacher != request.user:
            return JsonResponse({'error': 'Permission denied.'}, status=403)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found.'}, status=404)

    total_lectures = Lecture.objects.filter(subject=subject).count()
    total_students = subject.class_obj.students.count()
    
    if total_lectures == 0 or total_students == 0:
        return JsonResponse({'present': 0, 'absent': 0})

    total_possible_attendances = total_students * total_lectures
    actual_attendances = Attendance.objects.filter(lecture__subject=subject, status='approved').count()

    return JsonResponse({
        'present': actual_attendances,
        'absent': total_possible_attendances - actual_attendances
    })


@login_required
def get_student_attendance_percentages(request):
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Subject ID is required.'}, status=400)

    try:
        subject = Subject.objects.get(pk=subject_id)
        if request.user.role == 'Teacher' and subject.teacher != request.user:
            return JsonResponse({'error': 'Permission denied.'}, status=403)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found.'}, status=404)

    total_lectures = Lecture.objects.filter(subject=subject).count()
    if total_lectures == 0:
        return JsonResponse({'students': []})

    students = subject.class_obj.students.all()
    student_percentages = []
    for student in students:
        attended_count = Attendance.objects.filter(
            lecture__subject=subject,
            student=student,
            status='approved'
        ).count()
        percentage = (attended_count / total_lectures) * 100 if total_lectures > 0 else 0
        student_percentages.append({
            'name': student.name,
            'percentage': round(percentage)
        })

    return JsonResponse({'students': student_percentages})


@login_required
def reports_view(request):
    if request.user.role != 'Teacher':
        raise PermissionDenied
    
    try:
        active_session = AcademicSession.objects.get(is_active=True)
    except AcademicSession.DoesNotExist:
        messages.error(request, "There is no active academic session. Please contact an administrator.")
        return render(request, 'teacher/reports.html', {'courses_with_subjects': {}})

    subjects_taught = Subject.objects.filter(
        teacher=request.user,
        class_obj__session=active_session
    ).select_related('class_obj__course')

    courses_with_subjects = {}
    for subject in subjects_taught:
        course = subject.class_obj.course
        if course not in courses_with_subjects:
            courses_with_subjects[course] = []
        courses_with_subjects[course].append(subject)

    context = {
        'courses_with_subjects': courses_with_subjects,
    }
    return render(request, 'teacher/reports.html', context)

@login_required
def get_classes(request, course_id):
    if request.user.role != 'Teacher':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        active_session = AcademicSession.objects.get(is_active=True)
    except AcademicSession.DoesNotExist:
        return JsonResponse({'error': 'No active session'}, status=400)

    classes = Class.objects.filter(course_id=course_id, session=active_session).values('id', 'name')
    return JsonResponse({'classes': list(classes)})

@login_required
def search_students(request, lecture_id):
    if request.user.role != 'Teacher':
        return JsonResponse({'error': 'Permission denied'}, status=403)

    query = request.GET.get('query', '')
    lecture = get_object_or_404(Lecture, pk=lecture_id)

    # Ensure the teacher is authorized for this lecture
    if lecture.subject.teacher != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get students enrolled in the lecture's class
    enrolled_students = lecture.subject.class_obj.students.all()

    # Filter by name or roll number
    if query:
        students = enrolled_students.filter(
            Q(name__icontains=query) | Q(roll_no__icontains=query)
        )
    else:
        students = CustomUser.objects.none() # Return no students if query is empty

    # Get attendance status for all students in the class for this lecture
    attendance_records = Attendance.objects.filter(
        lecture=lecture,
        student__in=enrolled_students
    ).values('student_id', 'status')

    attendance_status_map = {rec['student_id']: rec['status'] for rec in attendance_records}

    student_data = []
    for student in students:
        status = attendance_status_map.get(student.id)
        student_data.append({
            'id': student.id,
            'name': student.name,
            'roll_no': student.roll_no,
            'attendance_status': status # Will be 'pending', 'approved', 'rejected', or None
        })

    return JsonResponse({'students': student_data})

from student.email import send_attendance_confirmation_email

@login_required
@require_POST
def manual_mark_attendance(request, lecture_id):
    if request.user.role != 'Teacher':
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    lecture = get_object_or_404(Lecture, pk=lecture_id)

    # Ensure the teacher is authorized for this lecture
    if lecture.subject.teacher != request.user:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    student_id = request.POST.get('student_id')
    if not student_id:
        return JsonResponse({'success': False, 'message': 'Student ID not provided.'})

    student = get_object_or_404(CustomUser, pk=student_id, role='Student')

    # Check if the student is enrolled in the class
    if not lecture.subject.class_obj.students.filter(pk=student.id).exists():
        return JsonResponse({'success': False, 'message': 'Student not enrolled in this class.'})

    # Use get_or_create to mark attendance, preventing duplicates
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        lecture=lecture,
        defaults={'subject': lecture.subject, 'date': lecture.date, 'status': 'approved'}
    )

    if created:
        return JsonResponse({'success': True, 'message': f'Attendance marked for {student.name}.'})
    else:
        # If attendance already existed, ensure it's marked as approved
        if attendance.status != 'approved':
            attendance.status = 'approved'
            attendance.save()
        return JsonResponse({'success': True, 'message': f'Attendance for {student.name} is now approved.'})


@login_required
def get_pending_attendance(request, lecture_id):
    if request.user.role != 'Teacher':
        return JsonResponse({'error': 'Permission denied'}, status=403)

    lecture = get_object_or_404(Lecture, pk=lecture_id)

    if lecture.subject.teacher != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    pending_attendances = Attendance.objects.filter(
        lecture=lecture,
        status='pending'
    ).select_related('student')

    student_data = [
        {
            'attendance_id': att.id,
            'student_id': att.student.id,
            'name': att.student.name,
            'roll_no': att.student.roll_no,
            'timestamp': att.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for att in pending_attendances
    ]

    return JsonResponse({'pending_students': student_data})


@login_required
@require_POST
def approve_attendance(request, attendance_id):
    if request.user.role != 'Teacher':
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    attendance = get_object_or_404(Attendance, pk=attendance_id)
    lecture = attendance.lecture

    if lecture.subject.teacher != request.user:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    attendance.status = 'approved'
    attendance.save()
    
    # Notify student
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"student_{attendance.student.id}",
        {
            "type": "attendance_status_update",
            "message": {
                "subject_name": lecture.subject.name,
                "status": "approved",
            }
        }
    )

    return JsonResponse({'success': True, 'message': 'Attendance approved.'})


@login_required
@require_POST
def reject_attendance(request, attendance_id):
    if request.user.role != 'Teacher':
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    attendance = get_object_or_404(Attendance, pk=attendance_id)
    lecture = attendance.lecture

    if lecture.subject.teacher != request.user:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        rejection_reason = data.get('reason', 'No reason provided.')
    except json.JSONDecodeError:
        rejection_reason = 'No reason provided.'

    attendance.status = 'rejected'
    attendance.rejection_reason = rejection_reason
    attendance.save()

    # Notify student
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"student_{attendance.student.id}",
        {
            "type": "attendance_status_update",
            "message": {
                "subject_name": lecture.subject.name,
                "status": "rejected",
                "reason": rejection_reason,
            }
        }
    )

    return JsonResponse({'success': True, 'message': 'Attendance rejected.'})

@login_required
@require_POST
def approve_all_attendance(request, lecture_id):
    if request.user.role != 'Teacher':
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    lecture = get_object_or_404(Lecture, pk=lecture_id)

    if lecture.subject.teacher != request.user:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    pending_attendances = Attendance.objects.filter(lecture=lecture, status='pending')
    
    for attendance in pending_attendances:
        attendance.status = 'approved'
        attendance.save()
        
        # Notify student
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"student_{attendance.student.id}",
            {
                "type": "attendance_status_update",
                "message": {
                    "subject_name": lecture.subject.name,
                    "status": "approved",
                }
            }
        )

    return JsonResponse({'success': True, 'message': 'All pending attendances have been approved.'})

