from django.contrib import admin
from .models import Course, Class, Attendance, QRCode

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'teacher')

admin.site.register(Course, CourseAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Attendance)
admin.site.register(QRCode)