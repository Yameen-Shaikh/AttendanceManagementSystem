from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from datetime import timedelta
from teacher.models import Lecture

class Command(BaseCommand):
    help = 'Deletes lecture records older than a specified number of days.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--days',
            type=int,
            default=1825, # Default to 5 years
            help='The number of days to keep lecture records. Records older than this will be deleted.'
        )

    def handle(self, *args, **options):
        days_to_keep = options['days']
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        self.stdout.write(f"Searching for lectures older than {cutoff_date.strftime('%Y-%m-%d')}...")

        # Query for old lectures
        old_lectures = Lecture.objects.filter(date__lt=cutoff_date)
        
        count = old_lectures.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No old lectures found to delete.'))
            return

        # Deleting the lectures will also delete associated attendance and QR codes due to `on_delete=models.CASCADE`
        old_lectures.delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old lecture record(s).'))
