from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_attendance_confirmation_email(student, lecture):
    """
    Sends a confirmation email to a student when their attendance is marked.
    """
    if not student.email:
        return

    subject = f"Attendance Confirmation for {lecture.subject.name}"
    
    context = {
        'student_name': student.name,
        'subject_name': lecture.subject.name,
        'class_name': lecture.subject.class_obj.name,
        'course_name': lecture.subject.class_obj.course.name,
        'lecture_date': lecture.date,
        'lecture_time': lecture.time,
    }
    
    # Render the email body from a text template
    body = render_to_string('student/email/attendance_confirmation.txt', context)
    
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL, # Use default from email
            [student.email],
            fail_silently=False,
        )
    except Exception as e:
        # Log the exception in a real application
        print(f"Error sending email to {student.email}: {e}")

