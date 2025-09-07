from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Course, Attendance, QRCode

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ('email',)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_code', 'teacher')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Attendance)
admin.site.register(QRCode)