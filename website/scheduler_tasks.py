from scheduler import job
from django.utils import timezone
from django.core.cache import cache
from .models import Paste
import logging

logger = logging.getLogger(__name__)


@job(schedule="*/10 * * * *")  # Every 10 minutes
def cleanup_expired_pastes():
    """
    Clean up expired pastes and one-time pastes that have been viewed.
    This task runs every 10 minutes via django-tasks-scheduler.
    """
    try:
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
        
        # Remove duplicates
        pastes_to_delete = pastes_to_delete.distinct()
        
        count = pastes_to_delete.count()
        
        if count > 0:
            # Store paste IDs for cache cleanup
            paste_ids = list(pastes_to_delete.values_list('id', flat=True))
            
            # Delete the pastes
            pastes_to_delete.delete()
            
            # Clear related cache entries
            for paste_id in paste_ids:
                cache_key = f'paste_{paste_id}'
                cache.delete(cache_key)
            
            logger.info(f"Automated cleanup: Deleted {count} expired/one-time pastes")
        else:
            logger.debug("Automated cleanup: No pastes to delete")
            
        return f"Cleaned up {count} pastes"
        
    except Exception as e:
        logger.error(f"Error during automated paste cleanup: {e}")
        raise


@job
def cleanup_single_paste(paste_id):
    """
    Clean up a specific paste by ID.
    Useful for immediate cleanup of expired pastes.
    """
    try:
        paste = Paste.objects.get(id=paste_id)
        
        # Check if paste should be deleted
        now = timezone.now()
        should_delete = False
        
        if paste.expires and paste.expires < now:
            should_delete = True
        elif paste.one_time and paste.view_count > 1:
            should_delete = True
        
        if should_delete:
            paste.delete()
            cache.delete(f'paste_{paste_id}')
            logger.info(f"Deleted paste {paste_id}")
            return f"Deleted paste {paste_id}"
        else:
            logger.debug(f"Paste {paste_id} does not need cleanup")
            return f"Paste {paste_id} does not need cleanup"
            
    except Paste.DoesNotExist:
        logger.warning(f"Paste {paste_id} not found for cleanup")
        return f"Paste {paste_id} not found"
    except Exception as e:
        logger.error(f"Error cleaning up paste {paste_id}: {e}")
        raise


@job(schedule="0 2 * * *")  # Every day at 2 AM
def optimize_database():
    """
    Optimize database by running maintenance tasks.
    This should be run periodically to maintain performance.
    """
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Run VACUUM to reclaim space and optimize (for SQLite)
            cursor.execute("VACUUM")
            logger.info("Database VACUUM completed")
            
            # Run ANALYZE to update statistics (for SQLite)
            cursor.execute("ANALYZE")
            logger.info("Database ANALYZE completed")
        
        logger.info("Database optimization completed")
        return "Database optimization completed"
        
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        raise 