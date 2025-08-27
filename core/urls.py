from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/generate-qr/', views.generate_qr_code, name='generate_qr_code'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('login/', views.login_view, name='login'),
]
