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

class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    lecture_date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.class_field.name} ({self.class_field.course.name}) - {self.lecture_date}"

class QRCode(models.Model):
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    qr_code_data = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"QRCode for {self.class_field.name} ({self.class_field.course.name})"