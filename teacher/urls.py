"""
URL configuration for the teacher app.
"""

from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('register/', views.teacher_register_view, name='register'),
    path('course/create/', views.create_course_view, name='create_course'),
    path('course/<int:course_id>/class/create/', views.create_class_view, name='create_class'),
    path('class/<int:class_id>/schedule-lecture/', views.schedule_lecture_view, name='schedule_lecture'),
    path('class/<int:class_id>/lectures/', views.view_lectures, name='view_lectures'),
    path('lectures/prune/', views.prune_lectures_view, name='prune_lectures'),
    path('lecture/<int:lecture_id>/generate-qr/', views.generate_qr_code, name='generate_qr_code'),
    path('class/<int:class_id>/report/', views.view_report, name='view_report'),
    path('profile/', views.profile, name='profile'),
    path('course/update/<int:course_id>/', views.update_course_view, name='update_course'),
    path('course/delete/<int:course_id>/', views.delete_course_view, name='delete_course'),
    path('class/update/<int:class_id>/', views.update_class_view, name='update_class'),
    path('class/delete/<int:class_id>/', views.delete_class_view, name='delete_class'),
    path('class/<int:class_id>/attendance-data/', views.get_attendance_data, name='get_attendance_data'),
    path('reports/', views.reports_view, name='reports'),
]