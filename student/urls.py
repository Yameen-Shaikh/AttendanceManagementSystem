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
    path('scan-qr/<int:class_id>/', views.scan_qr_code, name='scan_qr_code'),
    path('profile/', views.profile, name='profile'),
]