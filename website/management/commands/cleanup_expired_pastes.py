from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache
from website.models import Paste
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up expired pastes and one-time pastes that have been viewed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about what is being cleaned',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if verbose:
            self.stdout.write("Starting paste cleanup...")
        
        # Get current time
        now = timezone.now()
        
        # Find expired pastes
        expired_pastes = Paste.objects.filter(
            expires__lt=now
        )
        
        # Find one-time pastes that have been viewed more than once
        one_time_viewed_pastes = Paste.objects.filter(
            one_time=True,
            view_count__gt=1
        )
        
        # Combine both querysets
        pastes_to_delete = expired_pastes | one_time_viewed_pastes
        
        # Remove duplicates (in case a paste is both expired and one-time viewed)
        pastes_to_delete = pastes_to_delete.distinct()
        
        count = pastes_to_delete.count()
        
        if verbose:
            self.stdout.write(f"Found {expired_pastes.count()} expired pastes")
            self.stdout.write(f"Found {one_time_viewed_pastes.count()} one-time pastes that have been viewed")
            self.stdout.write(f"Total pastes to delete: {count}")
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("No pastes to clean up!")
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would delete {count} pastes")
            )
            if verbose:
                for paste in pastes_to_delete[:10]:  # Show first 10
                    self.stdout.write(f"  - Paste {paste.id} (created: {paste.created})")
                if count > 10:
                    self.stdout.write(f"  ... and {count - 10} more")
        else:
            # Delete the pastes
            pastes_to_delete.delete()
            
            # Clear related cache entries
            for paste in pastes_to_delete:
                cache_key = f'paste_{paste.id}'
                cache.delete(cache_key)
            
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {count} pastes")
            )
            
            if verbose:
                self.stdout.write("Cleanup completed successfully!")
        
        # Log the cleanup
        logger.info(f"Paste cleanup completed: {count} pastes {'would be ' if dry_run else ''}deleted") 