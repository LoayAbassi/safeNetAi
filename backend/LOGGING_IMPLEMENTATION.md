# SafeNetAi Logging System Implementation

## Overview

This document outlines the comprehensive logging system implemented for SafeNetAi, providing detailed logging across all major modules with proper categorization, security, and monitoring capabilities.

## Features Implemented

### ✅ 1. Multi-Module Logging
- **Authentication** → `logs/auth.log`
- **AI/ML Predictions** → `logs/ai.log`
- **Rule-based Engine** → `logs/rules.log`
- **Transactions** → `logs/transactions.log`
- **General System** → `logs/system.log`
- **Errors** → `logs/errors.log`

### ✅ 2. Advanced Logging Configuration
- **TimedRotatingFileHandler**: Daily rotation with 7 backup files
- **Consistent Format**: `[timestamp] [level] [module] message`
- **Environment-based Configuration**: All log levels configurable via `.env`
- **Automatic File Creation**: Log files created automatically if not present

### ✅ 3. Comprehensive Action Logging
- **Authentication**: Login, logout, failed login, registration, OTP verification
- **Transactions**: Creation, approval, rejection, balance updates
- **AI/ML**: Model loading, predictions, training, feature preparation
- **Rules Engine**: Rule evaluations, triggers, risk assessments
- **System Events**: Email sending, database operations, configuration changes

### ✅ 4. Security & Privacy
- **Sensitive Data Sanitization**: Passwords, tokens, secrets automatically redacted
- **Structured Logging**: Consistent format with optional extra data
- **Error Handling**: Comprehensive error logging without exposing sensitive information

### ✅ 5. Admin Log Viewer (React)
- **Real-time Log Viewing**: Browse logs by type and level
- **Advanced Filtering**: Search, pagination, level filtering
- **System Monitoring**: Database, email, and system status
- **Log Statistics**: File sizes, line counts, modification times

## Technical Implementation

### Backend Architecture

#### 1. Logging Configuration (`settings.py`)
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '[{asctime}] [{levelname}] [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'auth_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'auth.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
        },
        # ... similar for other log types
    },
    'loggers': {
        'auth': {'handlers': ['console', 'auth_file', 'error_file']},
        'ai': {'handlers': ['console', 'ai_file', 'error_file']},
        'rules': {'handlers': ['console', 'rules_file', 'error_file']},
        'transactions': {'handlers': ['console', 'transactions_file', 'error_file']},
        'system': {'handlers': ['console', 'system_file', 'error_file']},
    }
}
```

#### 2. Centralized Logging Utility (`apps/utils/logger.py`)
```python
class SafeNetLogger:
    def _sanitize_data(self, data: Any) -> Any:
        # Automatically redacts sensitive information
        sensitive_keys = ['password', 'token', 'secret', 'key', 'credential']
        # ... sanitization logic
    
    def info(self, message: str, extra_data: Optional[Dict] = None):
        # Structured logging with optional extra data
```

#### 3. Convenience Functions
```python
def log_user_action(action: str, user_id: int, user_email: str, success: bool):
    # Standardized user action logging

def log_prediction(model_name: str, input_data: Dict, prediction: Any, confidence: float):
    # AI/ML prediction logging

def log_rule_evaluation(rule_name: str, transaction_id: int, triggered: bool, risk_score: float):
    # Rule engine evaluation logging

def log_transaction(transaction_id: int, amount: float, transaction_type: str, user_id: int, status: str):
    # Transaction event logging
```

### Frontend Implementation

#### 1. Log Viewer Component (`frontend/src/pages/admin/Logs.jsx`)
- **Tabbed Interface**: Logs, Statistics, System Info
- **Advanced Filtering**: Log type, level, search, pagination
- **Real-time Updates**: Refresh functionality
- **Responsive Design**: Mobile-friendly interface

#### 2. API Endpoints (`apps/system/views.py`)
```python
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_logs(request):
    # Paginated log viewing with filtering

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_log_stats(request):
    # Log file statistics

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_info(request):
    # System health monitoring
```

## Module-Specific Logging

### Authentication Module
- **Login Success/Failure**: User ID, email, IP address, success status
- **Registration**: New user creation, OTP generation
- **OTP Verification**: Success/failure, expiration handling
- **Security Events**: Rate limiting, suspicious activity

### Transaction Module
- **Transaction Creation**: Amount, type, user, initial status
- **Risk Assessment**: Risk score, triggers, ML contribution
- **Balance Updates**: Before/after balances, transaction types
- **Fraud Alerts**: Alert creation, email notifications

### AI/ML Module
- **Model Operations**: Loading, training, saving
- **Predictions**: Input features, scores, processing time
- **Feature Engineering**: Feature preparation, scaling
- **Performance Metrics**: Accuracy, anomaly detection rates

### Rules Engine
- **Rule Evaluations**: Rule name, triggered status, risk contribution
- **Threshold Checks**: Amount limits, frequency analysis
- **Location Analysis**: Distance calculations, anomaly detection
- **Statistical Analysis**: Z-scores, outlier detection

### System Module
- **Email Operations**: SMTP connections, send success/failure
- **Database Operations**: Connection status, query performance
- **Configuration**: Settings validation, environment checks
- **Error Handling**: Exception logging, stack traces

## Environment Configuration

### Required Environment Variables
```bash
# Logging Configuration
LOG_LEVEL_ROOT=WARNING
LOG_LEVEL_CONSOLE=INFO
LOG_LEVEL_AUTH=INFO
LOG_LEVEL_AI=INFO
LOG_LEVEL_RULES=INFO
LOG_LEVEL_TRANSACTIONS=INFO
LOG_LEVEL_SYSTEM=INFO
LOG_LEVEL_DJANGO=INFO
LOG_LEVEL_DJANGO_REQUEST=WARNING
LOG_LEVEL_DJANGO_SECURITY=WARNING
```

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about program execution
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical errors that may prevent the program from running

## Security Considerations

### Data Sanitization
- **Automatic Redaction**: Passwords, tokens, secrets, credentials
- **Structured Logging**: Consistent format prevents data leakage
- **Access Control**: Admin-only log viewing
- **Audit Trail**: Complete action history for security analysis

### Privacy Protection
- **PII Handling**: Email addresses and user IDs logged appropriately
- **Sensitive Data**: Financial amounts logged without exposing account details
- **Error Messages**: Generic error messages without exposing system internals

## Monitoring & Maintenance

### Log Rotation
- **Daily Rotation**: New log file created each day
- **7-Day Retention**: Automatic cleanup of old log files
- **Size Management**: Prevents disk space issues
- **Backup Strategy**: Preserves historical data

### Performance Impact
- **Asynchronous Logging**: Non-blocking log operations
- **Efficient Parsing**: Optimized log file reading
- **Pagination**: Large log files handled efficiently
- **Caching**: System info cached to reduce API calls

## Usage Examples

### Backend Logging
```python
from apps.utils.logger import log_user_action, log_transaction

# Log user login
log_user_action("LOGIN", user.id, user.email, True, {"ip_address": request.META.get('REMOTE_ADDR')})

# Log transaction creation
log_transaction(transaction.id, amount, transaction_type, user.id, "CREATED", f"Score_{risk_score}")
```

### Frontend Integration
```javascript
// Fetch logs with filtering
const response = await api.get(`/system/logs/?log_type=auth&level=ERROR&page=1&limit=50`);

// Get system statistics
const stats = await api.get('/system/logs/stats/');
```

## Troubleshooting

### Common Issues
1. **Log Files Not Created**: Check directory permissions
2. **Empty Log Files**: Verify log levels in environment
3. **Performance Issues**: Check log file sizes and rotation
4. **Access Denied**: Ensure admin privileges for log viewing

### Debugging
1. **Check Log Levels**: Verify environment variables
2. **Monitor File Sizes**: Large log files may indicate issues
3. **Review Error Logs**: Check `logs/errors.log` for system issues
4. **Test Logging**: Use Django shell to test logging functions

## Future Enhancements

### Potential Improvements
1. **Log Aggregation**: Centralized log collection
2. **Real-time Alerts**: Automated alerting for critical events
3. **Log Analytics**: Advanced log analysis and reporting
4. **External Integration**: SIEM system integration
5. **Performance Metrics**: Log-based performance monitoring

### Scalability Considerations
1. **Database Logging**: Store logs in database for complex queries
2. **Distributed Logging**: Support for multiple server instances
3. **Log Compression**: Automatic compression of old log files
4. **Cloud Integration**: Cloud-based log storage and analysis

## Conclusion

The SafeNetAi logging system provides comprehensive monitoring and debugging capabilities while maintaining security and performance. The implementation follows best practices for production logging systems and provides administrators with powerful tools for system monitoring and troubleshooting.

The system is designed to be:
- **Comprehensive**: Covers all major system components
- **Secure**: Protects sensitive information
- **Performant**: Minimal impact on system performance
- **Maintainable**: Easy to configure and extend
- **User-friendly**: Intuitive admin interface for log viewing

This logging system serves as a foundation for operational excellence and security monitoring in the SafeNetAi platform.
