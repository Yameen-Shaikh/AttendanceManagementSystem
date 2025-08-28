import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'email']

    def __str__(self):
        return self.username

class Course(models.Model):
    name = models.CharField(max_length=255)
    course_code = models.TextField(unique=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_taught', limit_choices_to={'role': 'Teacher'})
    students = models.ManyToManyField(CustomUser, related_name='enrolled_courses', limit_choices_to={'role': 'Student'})

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecture_date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.lecture_date}"

class QRCode(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    qr_code_data = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(Sself):
        return f"QRCode for {self.course.name}"