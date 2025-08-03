from django.core.management.base import BaseCommand
from scheduler.scheduler import Scheduler


class Command(BaseCommand):
    help = 'Run the django-tasks-scheduler'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting django-tasks-scheduler...')
        )
        
        try:
            scheduler = Scheduler()
            scheduler.run()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Scheduler stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Scheduler error: {e}')
            ) 