"""
System management views for SafeNetAi
Includes log viewing and system monitoring
"""

import os
import json
from pathlib import Path
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_logs(request):
    """
    Get logs with pagination and filtering
    Query parameters:
    - log_type: auth, ai, rules, transactions, system, errors
    - level: INFO, WARNING, ERROR, CRITICAL
    - page: page number for pagination
    - limit: number of entries per page
    - search: search term in log messages
    """
    try:
        # Get query parameters
        log_type = request.GET.get('log_type', 'system')
        level = request.GET.get('level', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 50))
        search = request.GET.get('search', '')
        
        # Validate log type
        valid_log_types = ['auth', 'ai', 'rules', 'transactions', 'system', 'errors']
        if log_type not in valid_log_types:
            return Response({
                'error': f'Invalid log type. Must be one of: {", ".join(valid_log_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine log file path
        log_filename = f"{log_type}.log"
        log_path = Path(settings.LOGS_DIR) / log_filename
        
        if not log_path.exists():
            return Response({
                'error': f'Log file {log_filename} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Read log file
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse and filter log entries
        log_entries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse log line format: [timestamp] [level] [name] message
            try:
                if line.startswith('['):
                    # Extract timestamp
                    timestamp_end = line.find(']', 1)
                    if timestamp_end == -1:
                        continue
                    timestamp = line[1:timestamp_end]
                    
                    # Extract level
                    level_start = line.find('[', timestamp_end)
                    if level_start == -1:
                        continue
                    level_start += 1
                    level_end = line.find(']', level_start)
                    if level_end == -1:
                        continue
                    log_level = line[level_start:level_end]
                    
                    # Extract name
                    name_start = line.find('[', level_end)
                    if name_start == -1:
                        continue
                    name_start += 1
                    name_end = line.find(']', name_start)
                    if name_end == -1:
                        continue
                    name = line[name_start:name_end]
                    
                    # Extract message
                    message = line[name_end + 1:].strip()
                    
                    # Apply filters
                    if level and log_level != level:
                        continue
                    if search and search.lower() not in message.lower():
                        continue
                    
                    log_entries.append({
                        'timestamp': timestamp,
                        'level': log_level,
                        'name': name,
                        'message': message,
                        'raw_line': line
                    })
            except Exception:
                # Skip malformed lines
                continue
        
        # Reverse to show newest first
        log_entries.reverse()
        
        # Paginate results
        paginator = Paginator(log_entries, limit)
        page_obj = paginator.get_page(page)
        
        return Response({
            'log_type': log_type,
            'total_entries': len(log_entries),
            'total_pages': paginator.num_pages,
            'current_page': page,
            'entries_per_page': limit,
            'entries': page_obj.object_list,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
        
    except Exception as e:
        return Response({
            'error': f'Error reading logs: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_log_stats(request):
    """Get statistics about log files"""
    try:
        logs_dir = Path(settings.LOGS_DIR)
        stats = {}
        
        log_files = ['auth.log', 'ai.log', 'rules.log', 'transactions.log', 'system.log', 'errors.log']
        
        for log_file in log_files:
            log_path = logs_dir / log_file
            if log_path.exists():
                # Get file size
                size = log_path.stat().st_size
                
                # Count lines
                with open(log_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                # Get last modified time
                mtime = log_path.stat().st_mtime
                
                stats[log_file.replace('.log', '')] = {
                    'size_bytes': size,
                    'size_mb': round(size / (1024 * 1024), 2),
                    'line_count': line_count,
                    'last_modified': mtime,
                    'exists': True
                }
            else:
                stats[log_file.replace('.log', '')] = {
                    'exists': False
                }
        
        return Response(stats)
        
    except Exception as e:
        return Response({
            'error': f'Error getting log stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_info(request):
    """Get system information and status"""
    try:
        from django.db import connection
        from django.core.cache import cache
        
        # Database info
        db_info = {
            'engine': settings.DATABASES['default']['ENGINE'],
            'name': settings.DATABASES['default'].get('NAME', 'N/A'),
        }
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_info['status'] = 'connected'
        except Exception as e:
            db_info['status'] = 'error'
            db_info['error'] = str(e)
        
        # Cache info
        cache_info = {
            'backend': settings.CACHES['default']['BACKEND'] if hasattr(settings, 'CACHES') else 'N/A',
            'status': 'working' if cache.get('test_key') is None else 'error'
        }
        
        # Email info
        email_info = {
            'backend': settings.EMAIL_BACKEND,
            'host': settings.EMAIL_HOST,
            'port': settings.EMAIL_PORT,
            'tls': settings.EMAIL_USE_TLS,
            'ssl': getattr(settings, 'EMAIL_USE_SSL', False),
            'user_configured': bool(settings.EMAIL_HOST_USER),
            'password_configured': bool(settings.EMAIL_HOST_PASSWORD)
        }
        
        # Logging info
        logging_info = {
            'log_level_root': getattr(settings, 'LOG_LEVEL_ROOT', 'WARNING'),
            'log_level_console': getattr(settings, 'LOG_LEVEL_CONSOLE', 'INFO'),
            'logs_directory': str(settings.LOGS_DIR)
        }
        
        return Response({
            'database': db_info,
            'cache': cache_info,
            'email': email_info,
            'logging': logging_info,
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
        })
        
    except Exception as e:
        return Response({
            'error': f'Error getting system info: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
