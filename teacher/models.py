import uuid
from django.db import models
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="e.g., 'B.Sc. Computer Science'")

    def __str__(self):
        return self.name

class AcademicSession(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., '2025-2026'")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True, help_text="Indicates if this is the current, active session.")

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., 'First Year'") # e.g., "First Year"
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    session = models.ForeignKey(AcademicSession, on_delete=models.PROTECT, related_name="classes")
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_classes', limit_choices_to={'role': 'Student'}, blank=True)

    class Meta:
        verbose_name_plural = "Classes" # Fixes admin display name
        unique_together = ('course', 'name', 'session')

    def __str__(self):
        return f"{self.course.name} - {self.name} ({self.session.name})"

class Subject(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., 'Introduction to Programming'")
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subjects_taught', limit_choices_to={'role': 'Teacher'})

    def __str__(self):
        return f"{self.name} ({self.class_obj})"


class Lecture(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lectures')
    date = models.DateField()
    time = models.TimeField()
    is_archived = models.BooleanField(default=False, help_text="Set to true to hide from active lists.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lecture for {self.subject.name} ({self.subject.class_obj.name}) on {self.date} at {self.time}"


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, related_name='attendances', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        lecture_info = self.lecture if self.lecture else f"{self.subject.name if self.subject else 'Unknown'} on {self.date}"
        return f"{self.student.name} - {lecture_info} ({self.get_status_display()})"

class HistoricalAttendance(Attendance):
    class Meta:
        proxy = True
        verbose_name = 'Historical Attendance Record'
        verbose_name_plural = 'Historical Attendance Records'



class QRCode(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='qr_codes', null=True, blank=True)
    qr_code_data = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"QRCode for {self.lecture}"