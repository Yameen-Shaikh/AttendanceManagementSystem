from django.contrib import admin
from django.urls import path, include
from student import views as student_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', student_views.login_view, name='login'),
    path('logout/', student_views.logout_view, name='logout'),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
]