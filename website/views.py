import hashlib
import random
import re
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Paste, Language
from .encryption import encrypt, decrypt
from django.core.cache import cache
from django.conf import settings

def detect_language_from_content(content):
    """Detect programming language from content using patterns and keywords"""
    if not content or not content.strip():
        return None
    
    content_lower = content.lower()
    lines = content.split('\n')
    first_line = lines[0].lower() if lines else ""
    
    # Check for shebang
    if first_line.startswith('#!'):
        if 'python' in first_line:
            return 'python'
        elif 'bash' in first_line or 'sh' in first_line:
            return 'bash'
        elif 'node' in first_line:
            return 'javascript'
    
    # Language patterns and keywords (ordered by specificity)
    language_patterns = {
        'html': {
            'patterns': [r'<!DOCTYPE html>', r'<html[^>]*>', r'<head[^>]*>', r'<body[^>]*>', r'</html>', r'\.html$'],
            'keywords': ['<!DOCTYPE', '<html', '<head', '<body', '<div', '<span', '<p', '<a', '<script', '<style'],
            'weight': 20
        },
        'css': {
            'patterns': [r'\.\w+\s*\{', r'@media\s*\(', r'@import\s+url', r'\.css$'],
            'keywords': ['{', '}', ':', ';', '@media', '@import', 'background', 'color', 'font', 'margin', 'padding', 'display', 'position'],
            'weight': 15
        },
        'javascript': {
            'patterns': [r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'var\s+\w+\s*=', r'console\.log', r'\.js$'],
            'keywords': ['function', 'const', 'let', 'var', 'console.log', '=>', 'async', 'await', 'export', 'import', 'return', 'if', 'else'],
            'weight': 15
        },
        'python': {
            'patterns': [r'^#!/.*python', r'import\s+\w+', r'from\s+\w+\s+import', r'def\s+\w+\s*\(', r'class\s+\w+', r'\.py$'],
            'keywords': ['def', 'class', 'import', 'from', 'if __name__', 'print', 'return', 'self', 'True', 'False', 'None', 'try', 'except'],
            'weight': 15
        },
        'php': {
            'patterns': [r'<\?php', r'\$\w+\s*=', r'echo\s+', r'function\s+\w+', r'\.php$'],
            'keywords': ['<?php', 'echo', '$', 'function', 'class', 'namespace', 'use', 'return', 'if', 'else'],
            'weight': 12
        },
        'sql': {
            'patterns': [r'SELECT\s+.*FROM', r'INSERT\s+INTO', r'UPDATE\s+\w+\s+SET', r'DELETE\s+FROM', r'CREATE\s+TABLE', r'\.sql$'],
            'keywords': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY'],
            'weight': 12
        },
        'java': {
            'patterns': [r'public\s+class\s+\w+', r'import\s+java\.', r'System\.out\.print', r'public\s+static\s+void\s+main', r'\.java$'],
            'keywords': ['public', 'class', 'import', 'System.out', 'static', 'void', 'String', 'int', 'private', 'protected'],
            'weight': 12
        },
        'cpp': {
            'patterns': [r'#include\s*<[^>]+>', r'using\s+namespace\s+std', r'std::', r'int\s+main\s*\(', r'\.cpp$'],
            'keywords': ['#include', 'using namespace', 'std::', 'cout', 'cin', 'int main', 'vector', 'string', 'class'],
            'weight': 10
        },
        'bash': {
            'patterns': [r'#!/bin/bash', r'#!/bin/sh', r'echo\s+["\']', r'if\s+\[.*\];\s+then', r'for\s+\w+\s+in', r'\.sh$'],
            'keywords': ['#!/bin', 'echo', 'if [', 'for', 'while', 'do', 'done', 'then', 'fi', 'exit'],
            'weight': 10
        },
        'json': {
            'patterns': [r'^\s*\{.*\}$', r'^\s*\[.*\]$', r'"[\w-]+"\s*:', r'\.json$'],
            'keywords': ['{', '}', '[', ']', ':', '"', 'true', 'false', 'null'],
            'weight': 8
        },
        'xml': {
            'patterns': [r'<\?xml[^>]*\?>', r'<[^>]+>.*</[^>]+>', r'<[^>]+/>', r'\.xml$'],
            'keywords': ['<?xml', '<', '>', '</', 'version=', 'encoding='],
            'weight': 8
        },
        'yaml': {
            'patterns': [r'^\s*\w+:\s*[^#\n]*$', r'^\s*-\s+\w+', r'^\s*#.*$', r'\.yml$', r'\.yaml$'],
            'keywords': [':', '-', 'version:', 'name:', 'description:', '#'],
            'weight': 8
        },
        'markdown': {
            'patterns': [r'^#\s+\w+', r'^\*\s+\w+', r'^-\s+\w+', r'\*\*[^*]+\*\*', r'__[^_]+__', r'\.md$'],
            'keywords': ['#', '*', '-', '##', '###', '**', '__', '```'],
            'weight': 6
        },
        'c': {
            'patterns': [r'#include\s*<[^>]+>', r'int\s+main\s*\(', r'printf\s*\(', r'scanf\s*\(', r'\.c$'],
            'keywords': ['#include', 'int main', 'printf', 'scanf', 'malloc', 'free', 'struct', 'return'],
            'weight': 5  # Lower weight to avoid false positives
        }
    }
    
    # Score each language
    scores = {}
    for lang, config in language_patterns.items():
        score = 0
        weight = config.get('weight', 1)
        
        # Check patterns
        for pattern in config['patterns']:
            if re.search(pattern, content, re.IGNORECASE):
                score += 10 * weight
        
        # Check keywords
        for keyword in config['keywords']:
            # Escape regex special characters
            escaped_keyword = re.escape(keyword)
            matches = len(re.findall(rf'\b{escaped_keyword}\b', content, re.IGNORECASE))
            score += matches * weight
        
        if score > 0:
            scores[lang] = score
    
    # Return the language with the highest score
    if scores:
        return max(scores, key=scores.get)
    
    return None

def get_cached_languages():
    """Get languages from cache or database"""
    languages = cache.get(settings.LANGUAGE_CACHE_KEY)
    if languages is None:
        languages = list(Language.objects.all().order_by('displayname'))
        cache.set(settings.LANGUAGE_CACHE_KEY, languages, settings.LANGUAGE_CACHE_TIMEOUT)
    return languages

def generate_unique_id():
    while True:
        unique_string = f"{timezone.now().timestamp()}{random.randint(0, 999999)}"
        hash_object = hashlib.sha256(unique_string.encode())
        unique_id = hash_object.hexdigest()[:6]
        if not Paste.objects.filter(id=unique_id).exists():
            return unique_id

def pasteCheck(paste):
    if paste.one_time and paste.view_count > 1:
        return False
    if paste.expires and paste.expires < timezone.now():
        return False
    return True

def home(request):
    """Home page showing recent pastes and create paste form"""
    # Get recent pastes from cookie history
    pastes = []
    pastes_cookie = request.COOKIES.get('pasteHistory', '')
    if pastes_cookie:
        paste_ids = pastes_cookie.split(',')
        # Get the most recent 10 pastes with select_related for better performance
        recent_pastes = Paste.objects.select_related('lang').filter(
            id__in=paste_ids
        ).order_by('-created')[:10]
        pastes = recent_pastes
    
    return render(request, 'home.html', {'pastes': pastes})

def create_paste(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        password = request.POST.get('password')
        language_id = request.POST.get('language')
        expiration_days = request.POST.get('expiration')
        one_time = request.POST.get('one_time') == 'on'
        
        # Handle auto language detection
        if language_id == 'auto':
            # Simple language detection based on content
            detected_lang = detect_language_from_content(content)
            if detected_lang:
                try:
                    lang = Language.objects.get(alias__iexact=detected_lang)
                except Language.DoesNotExist:
                    # Fallback to first available language if detected language not found
                    lang = Language.objects.first()
            else:
                # Default to first available language if no language detected
                lang = Language.objects.first()
            
            # Safety check - if no languages exist, create a default one
            if not lang:
                lang, created = Language.objects.get_or_create(
                    displayname='Plain Text',
                    alias='plaintext',
                    defaults={'displayname': 'Plain Text', 'alias': 'plaintext'}
                )
        else:
            lang = get_object_or_404(Language, id=language_id)

        if content:
            id = generate_unique_id()
            expires = None
            use_cache = False
            if expiration_days:
                if expiration_days == '0.007':  # 10 minutes
                    expires = timezone.now() + timedelta(minutes=10)
                    use_cache = True
                elif expiration_days == '0.042':  # 1 hour
                    expires = timezone.now() + timedelta(hours=1)
                    use_cache = True
                else:
                    expires = timezone.now() + timedelta(days=float(expiration_days))
            if password:
                salt, iv, ciphertext = encrypt(content, password)
                Paste.objects.create(id=id, salt=salt, iv=iv, ciphertext=ciphertext, lang=lang, expires=expires,
                                     one_time=one_time)
            else:
                Paste.objects.create(id=id, salt=None, iv=None, ciphertext=content, lang=lang, expires=expires,
                                     one_time=one_time)
            if use_cache:
                cache.set(f'paste_{id}', True, timeout=600)  # 10 minutes
            pastes_cookie = request.COOKIES.get('pasteHistory', '')
            if pastes_cookie:
                pastes_list = pastes_cookie.split(',')
                if id not in pastes_list:
                    pastes_list.append(id)
            else:
                pastes_list = [id]

            response = redirect('view_encrypted_paste', paste_id=id)
            response.set_cookie('pasteHistory', ','.join(pastes_list), max_age=31536000)
            return response

    # Use cached languages for better performance
    languages = get_cached_languages()
    return render(request, 'create.html', {'languages': languages})

def about(request):
    return render(request,'about.html')

def view_raw_paste(request, paste_id):
    try:
        paste = Paste.objects.get(id=paste_id)
    except Paste.DoesNotExist:
        return render(request, '404.html', status=404)

    # Check cache for 10-minute expiration
    if paste.expires and (paste.expires - paste.created).total_seconds() <= 601:
        if not cache.get(f'paste_{paste_id}'):
            paste.delete()
            return render(request, 'raw_clean.html', {'error': 'This paste is no longer available.'})

    if not pasteCheck(paste):
        paste.delete()
        return render(request, 'raw_clean.html', {'error': 'This paste is no longer available.'})

    if paste.salt:
        if request.method == 'POST':
            password = request.POST.get('password')
            if password:
                try:
                    decrypted_content = decrypt(paste.salt, paste.iv, paste.ciphertext, password)
                    paste.view_count += 1
                    paste.save()
                    return render(request, 'raw_clean.html', {'content': decrypted_content, 'lang': paste.lang})
                except Exception as e:
                    print(f"Decryption error: {e}")
                    return render(request, 'raw_clean.html', {'error': 'Incorrect password. Please try again.', 'lang': paste.lang})
        paste.view_count += 1
        paste.save()
        return render(request, 'raw_clean.html', {'lang': paste.lang, 'has_password': True})

    else:
        decrypted_content = paste.ciphertext
        paste.view_count += 1
        paste.save()
        return render(request, 'raw_clean.html', {'content': decrypted_content, 'lang': paste.lang})

def view_encrypted_paste(request, paste_id):
    try:
        paste = Paste.objects.get(id=paste_id)
    except Paste.DoesNotExist:
        return render(request, '404.html', status=404)

    # Check cache for 10-minute expiration
    if paste.expires and (paste.expires - paste.created).total_seconds() <= 601:
        if not cache.get(f'paste_{paste_id}'):
            paste.delete()
            return render(request, 'view.html', {'error': 'This paste is no longer available.'})

    if not pasteCheck(paste):
        paste.delete()
        return render(request, 'view.html', {'error': 'This paste is no longer available.'})

    if paste.salt:
        if request.method == 'POST':
            password = request.POST.get('password')
            if password:
                try:
                    decrypted_content = decrypt(paste.salt, paste.iv, paste.ciphertext, password)
                    paste.view_count += 1
                    paste.save()
                    return render(request, 'view.html', {'content': decrypted_content, 'lang': paste.lang, 'paste': paste})
                except Exception as e:
                    print(f"Decryption error: {e}")
                    return render(request, 'view.html', {'error': 'Incorrect password. Please try again.', 'lang': paste.lang, 'paste': paste})
        paste.view_count += 1
        paste.save()

        return render(request, 'view.html', {'lang': paste.lang, 'has_password': True, 'paste': paste})

    else:
        decrypted_content = paste.ciphertext
        paste.view_count += 1
        paste.save()

        return render(request, 'view.html', {'content': decrypted_content, 'lang': paste.lang, 'paste': paste})

def history(request):
    pastes = []
    pastes_cookie = request.COOKIES.get('pasteHistory', '')
    if pastes_cookie:
        paste_ids = pastes_cookie.split(',')
        # Use select_related to avoid N+1 queries
        pastes = Paste.objects.select_related('lang').filter(id__in=paste_ids).order_by('-created')
    return render(request, 'history.html', {'pastes': pastes})
def err404(request, exception):
    return render(request,'404.html',status=404)

