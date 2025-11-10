from django.contrib import admin
from django import forms
from .models import Course, Class, Attendance, QRCode, Subject

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

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ('name', 'course')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., First Year'}),
        }

class ClassAdmin(admin.ModelAdmin):
    form = ClassForm
    list_display = ('name', 'course')
    fields = ('name', 'course')

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

admin.site.register(Course, CourseAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Attendance)
admin.site.register(QRCode)