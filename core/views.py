from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Course, QRCode

@login_required
def generate_qr_code(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    # Optional: Add a check to ensure the user is the teacher for this course
    if request.user != course.teacher:
        return HttpResponseForbidden("You are not authorized to generate a QR code for this course.")

    expires_at = timezone.now() + timedelta(minutes=5)
    qr_code = QRCode.objects.create(course=course, expires_at=expires_at)
    
    context = {
        'course': course,
        'qr_code_data': str(qr_code.qr_code_data),
    }
    return render(request, 'generate_qr.html', context)