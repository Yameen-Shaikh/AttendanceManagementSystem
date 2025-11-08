import uuid
from django.db import models
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=255) # e.g., "First Year"
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classes_taught', limit_choices_to={'role': 'Teacher'})
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_classes', limit_choices_to={'role': 'Student'})
    subject = models.CharField(max_length=255, blank=True, null=True) # New field

    class Meta:
        verbose_name_plural = "Classes" # Fixes admin display name

    def __str__(self):
        return f"{self.course.name} - {self.name} ({self.subject})" # Updated __str__


class Lecture(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='lectures')
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lecture for {self.class_obj.name} on {self.date} at {self.time}"


class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.lecture}"


class QRCode(models.Model):
    lecture = models.OneToOneField(Lecture, on_delete=models.CASCADE, related_name='qr_code', null=True, blank=True)
    qr_code_data = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"QRCode for {self.lecture}"