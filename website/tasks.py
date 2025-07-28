from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from .models import Paste
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_pastes():
    """
    Clean up expired pastes and one-time pastes that have been viewed.
    This task runs every 10 minutes via Celery Beat.
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

@shared_task
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

@shared_task
def optimize_sqlite_database():
    """
    Optimize SQLite database by running VACUUM and ANALYZE.
    This should be run periodically to maintain performance.
    """
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Run VACUUM to reclaim space and optimize
            cursor.execute("VACUUM")
            logger.info("SQLite VACUUM completed")
            
            # Run ANALYZE to update statistics
            cursor.execute("ANALYZE")
            logger.info("SQLite ANALYZE completed")
        
        logger.info("SQLite database optimization completed")
        return "Database optimization completed"
        
    except Exception as e:
        logger.error(f"Error optimizing SQLite database: {e}")
        raise 