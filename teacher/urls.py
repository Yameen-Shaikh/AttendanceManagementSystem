"""
URL configuration for the teacher app.
"""

from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('register/', views.teacher_register_view, name='register'),
    path('select-class/', views.select_class_view, name='select_class'),
    path('class/<int:class_id>/create-subject/', views.create_subject_view, name='create_subject'),
    path('subject/<int:subject_id>/schedule-lecture/', views.schedule_lecture_view, name='schedule_lecture'),
    path('subject/<int:subject_id>/lectures/', views.view_lectures, name='view_lectures'),
    path('lectures/prune/', views.prune_lectures_view, name='prune_lectures'),
    path('lecture/<int:lecture_id>/generate-qr/', views.generate_qr_code, name='generate_qr_code'),
    path('lecture/<int:lecture_id>/search-students/', views.search_students, name='search_students'),
    path('lecture/<int:lecture_id>/mark-manual-attendance/', views.manual_mark_attendance, name='manual_mark_attendance'),
    path('lecture/<int:lecture_id>/pending-attendance/', views.get_pending_attendance, name='get_pending_attendance'),
    path('attendance/<int:attendance_id>/approve/', views.approve_attendance, name='approve_attendance'),
    path('attendance/<int:attendance_id>/reject/', views.reject_attendance, name='reject_attendance'),
    path('lecture/<int:lecture_id>/approve-all/', views.approve_all_attendance, name='approve_all_attendance'),
    path('subject/<int:subject_id>/report/', views.view_report, name='view_report'),
    path('profile/', views.profile, name='profile'),
    path('get-classes/<int:course_id>/', views.get_classes, name='get_classes'),
    path('reports/', views.reports_view, name='reports'),
    path('get-teacher-subject-attendance-data/', views.get_teacher_subject_attendance_data, name='get_teacher_subject_attendance_data'),
    path('get-student-attendance-percentages/', views.get_student_attendance_percentages, name='get_student_attendance_percentages'),
]