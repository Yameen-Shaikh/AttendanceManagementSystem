import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None # Removed username field
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    subjects = models.TextField(blank=True, null=True) # Added subjects field

    objects = CustomUserManager()

    USERNAME_FIELD = 'email' # Changed to email
    REQUIRED_FIELDS = ['name'] # Updated required fields

    def __str__(self):
        return self.email # Changed to email

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

    def __str__(self):
        return f"QRCode for {self.course.name}"