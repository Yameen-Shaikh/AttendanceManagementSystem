from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/generate-qr/', views.generate_qr_code, name='generate_qr_code'),
]
