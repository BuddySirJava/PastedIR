#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastebinir.settings')
django.setup()

# Test Celery import
try:
    from pastebinir.celery import app
    print("✅ Celery app imported successfully!")
    
    # Test task discovery
    from website.tasks import cleanup_expired_pastes
    print("✅ Tasks imported successfully!")
    
    # Test task execution
    result = cleanup_expired_pastes.delay()
    print(f"✅ Task queued successfully! Task ID: {result.id}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 