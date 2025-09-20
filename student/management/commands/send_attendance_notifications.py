from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from student.models import Course, Attendance, CustomUser

class Command(BaseCommand):
    help = 'Sends email notifications to students marked absent or present.'

    def handle(self, *args, **options):
        today = timezone.now().date()

        # Get all courses that had a QR code generated today
        active_courses = Course.objects.filter(qrcode__created_at__date=today).distinct()

        for course in active_courses:
            # Get all students enrolled in the course
            enrolled_students = course.students.all()

            # Get all students who were present in this course today
            present_students = CustomUser.objects.filter(
                attendance__course=course,
                attendance__lecture_date=today,
                attendance__is_present=True
            )

            # Determine absent students
            absent_students = enrolled_students.exclude(id__in=present_students.values_list('id', flat=True))

            for student in absent_students:
                send_mail(
                    'Absence Notification',
                    f'Dear {student.name},\n\nYou were marked absent for the course "{course.name}" today, {today}.\n\nPlease contact your teacher if you believe this is an error.',
                    'from@example.com',  # Replace with a sender email
                    [student.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Sent absence notification to {student.email} for course {course.name}'))

            for student in present_students:
                send_mail(
                    'Attendance Confirmation',
                    f'Dear {student.name},\n\nYour attendance for the course "{course.name}" on {today} has been successfully recorded.',
                    'from@example.com',  # Replace with a sender email
                    [student.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Sent presence notification to {student.email} for course {course.name}'))


        self.stdout.write(self.style.SUCCESS('Finished sending attendance notifications.'))
