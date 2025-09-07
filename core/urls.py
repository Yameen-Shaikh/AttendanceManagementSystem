from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('course/<int:course_id>/generate-qr/', views.generate_qr_code, name='generate_qr_code'),
    path('course/<int:course_id>/report/', views.view_report, name='view_report'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/scan-qr/', views.scan_qr_code, name='scan_qr_code'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
]
