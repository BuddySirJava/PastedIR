#!/usr/bin/env python
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastebinir.settings')

import django
django.setup()

def test_redis_connection():
    """Test Redis connection"""
    try:
        from django.core.cache import cache
        
        # Test basic cache operations
        cache.set('test_key', 'test_value', 60)
        value = cache.get('test_key')
        
        if value == 'test_value':
            print("✅ Redis cache connection successful!")
            cache.delete('test_key')
            return True
        else:
            print("❌ Redis cache test failed - value mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_celery_connection():
    """Test Celery connection"""
    try:
        from pastebinir.celery import app
        
        # Test Celery connection
        i = app.control.inspect()
        stats = i.stats()
        
        print("✅ Celery connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Celery connection failed: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Testing Redis and Celery connections...")
    
    redis_ok = test_redis_connection()
    celery_ok = test_celery_connection()
    
    if redis_ok and celery_ok:
        print("🎉 All connections successful!")
        sys.exit(0)
    else:
        print("❌ Some connections failed!")
        sys.exit(1) 