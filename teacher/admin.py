from django.contrib import admin
from django import forms
from .models import Course, Class, Attendance, QRCode, Subject, AcademicSession

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., BBA(CA)'}),
        }

class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    list_display = ('name',)

class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ('name', 'course', 'session')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., First Year'}),
        }

class ClassAdmin(admin.ModelAdmin):
    form = ClassForm
    list_display = ('name', 'course', 'session')
    list_filter = ('session',)
    fields = ('name', 'course', 'session')

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('name', 'class_obj', 'teacher')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Introduction to Programming'}),
        }

class SubjectAdmin(admin.ModelAdmin):
    form = SubjectForm
    list_display = ('name', 'class_obj', 'teacher')
    list_filter = ('class_obj__session',)

admin.site.register(Course, CourseAdmin)
admin.site.register(AcademicSession, AcademicSessionAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Subject, SubjectAdmin)
from .models import Course, Class, Attendance, QRCode, Subject, AcademicSession, HistoricalAttendance

class HistoricalAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'session')
    list_filter = ('subject__class_obj__session', 'subject', 'student')
    search_fields = ('student__name', 'student__email', 'subject__name')
    date_hierarchy = 'date'
    
    def session(self, obj):
        if obj.subject:
            return obj.subject.class_obj.session
        return None
    session.short_description = 'Academic Session'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(HistoricalAttendance, HistoricalAttendanceAdmin)
admin.site.register(QRCode)