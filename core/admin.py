from django.contrib import admin
from .models import CustomUser, Course, Attendance, QRCode

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_code', 'teacher')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Attendance)
admin.site.register(QRCode)