"""
URL configuration for the student app.
"""

from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('register/', views.student_register_view, name='register'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('scan-qr/', views.scan_qr_code, name='scan_qr_code'),
    path('profile/', views.profile, name='profile'),
    path('attendance-by-date/', views.get_attendance_by_date, name='get_attendance_by_date'),
    path('unenroll/<int:class_id>/', views.unenroll, name='unenroll'),
    path('enroll/<int:class_id>/', views.enroll, name='enroll'),
    path('reports/', views.reports, name='reports'),
    path('get-attendance-data/', views.get_attendance_data, name='get_attendance_data'),
]