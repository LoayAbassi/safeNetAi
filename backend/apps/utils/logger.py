"""
Logging utility module for SafeNetAi
Provides consistent logging across all modules with proper categorization
"""

import logging
import json
from typing import Any, Dict, Optional
from django.conf import settings
from django.utils import timezone


class SafeNetLogger:
    """
    Centralized logging utility for SafeNetAi
    Ensures consistent logging format and categorization
    """
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
    
    def _sanitize_data(self, data: Any) -> Any:
        """
        Remove sensitive information from data before logging
        """
        if isinstance(data, dict):
            sanitized = {}
            sensitive_keys = ['password', 'token', 'secret', 'key', 'credential']
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '***REDACTED***'
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data
    
    def _format_message(self, message: str, extra_data: Optional[Dict] = None) -> str:
        """
        Format log message with optional extra data
        """
        if extra_data:
            sanitized_data = self._sanitize_data(extra_data)
            return f"{message} | Data: {json.dumps(sanitized_data, default=str)}"
        return message
    
    def info(self, message: str, extra_data: Optional[Dict] = None):
        """Log info message"""
        self.logger.info(self._format_message(message, extra_data))
    
    def warning(self, message: str, extra_data: Optional[Dict] = None):
        """Log warning message"""
        self.logger.warning(self._format_message(message, extra_data))
    
    def error(self, message: str, extra_data: Optional[Dict] = None):
        """Log error message"""
        self.logger.error(self._format_message(message, extra_data))
    
    def debug(self, message: str, extra_data: Optional[Dict] = None):
        """Log debug message"""
        self.logger.debug(self._format_message(message, extra_data))
    
    def critical(self, message: str, extra_data: Optional[Dict] = None):
        """Log critical message"""
        self.logger.critical(self._format_message(message, extra_data))


# Module-specific logger factories
def get_auth_logger() -> SafeNetLogger:
    """Get authentication logger"""
    return SafeNetLogger('auth')

def get_ai_logger() -> SafeNetLogger:
    """Get AI/ML logger"""
    return SafeNetLogger('ai')

def get_rules_logger() -> SafeNetLogger:
    """Get rules engine logger"""
    return SafeNetLogger('rules')

def get_transactions_logger() -> SafeNetLogger:
    """Get transactions logger"""
    return SafeNetLogger('transactions')

def get_system_logger() -> SafeNetLogger:
    """Get system logger"""
    return SafeNetLogger('system')

def get_email_logger() -> SafeNetLogger:
    """Get email service logger"""
    return SafeNetLogger('email_service')


# Convenience functions for common logging scenarios
def log_user_action(action: str, user_id: int, user_email: str, success: bool, 
                   extra_data: Optional[Dict] = None):
    """
    Log user authentication actions
    """
    logger = get_auth_logger()
    status = "SUCCESS" if success else "FAILED"
    message = f"User action: {action} | User ID: {user_id} | Email: {user_email} | Status: {status}"
    logger.info(message, extra_data)

def log_prediction(model_name: str, input_data: Dict, prediction: Any, 
                  confidence: float, processing_time: float):
    """
    Log AI/ML predictions
    """
    logger = get_ai_logger()
    message = f"AI Prediction | Model: {model_name} | Confidence: {confidence:.2f} | Time: {processing_time:.3f}s"
    extra_data = {
        'model_name': model_name,
        'prediction': prediction,
        'confidence': confidence,
        'processing_time': processing_time
    }
    logger.info(message, extra_data)

def log_rule_evaluation(rule_name: str, transaction_id: int, triggered: bool, 
                       risk_score: float, triggers: list):
    """
    Log rule engine evaluations
    """
    logger = get_rules_logger()
    status = "TRIGGERED" if triggered else "NOT_TRIGGERED"
    message = f"Rule evaluation: {rule_name} | Transaction: {transaction_id} | Status: {status} | Risk Score: {risk_score}"
    extra_data = {
        'rule_name': rule_name,
        'transaction_id': transaction_id,
        'triggered': triggered,
        'risk_score': risk_score,
        'triggers': triggers
    }
    logger.info(message, extra_data)

def log_transaction(transaction_id: int, amount: float, transaction_type: str, 
                   user_id: int, status: str, risk_level: str = None):
    """
    Log transaction events
    """
    logger = get_transactions_logger()
    message = f"Transaction | ID: {transaction_id} | Amount: ${amount} | Type: {transaction_type} | Status: {status}"
    extra_data = {
        'transaction_id': transaction_id,
        'amount': amount,
        'transaction_type': transaction_type,
        'user_id': user_id,
        'status': status,
        'risk_level': risk_level
    }
    logger.info(message, extra_data)

def log_system_event(event: str, component: str, severity: str = 'INFO', 
                    extra_data: Optional[Dict] = None):
    """
    Log system events
    """
    logger = get_system_logger()
    message = f"System event: {event} | Component: {component} | Severity: {severity}"
    
    if severity.upper() == 'ERROR':
        logger.error(message, extra_data)
    elif severity.upper() == 'WARNING':
        logger.warning(message, extra_data)
    elif severity.upper() == 'CRITICAL':
        logger.critical(message, extra_data)
    else:
        logger.info(message, extra_data)

def log_security_event(event: str, user_id: Optional[int] = None, 
                      ip_address: Optional[str] = None, extra_data: Optional[Dict] = None):
    """
    Log security-related events
    """
    logger = get_auth_logger()
    message = f"Security event: {event}"
    if user_id:
        message += f" | User ID: {user_id}"
    if ip_address:
        message += f" | IP: {ip_address}"
    
    extra_data = extra_data or {}
    if user_id:
        extra_data['user_id'] = user_id
    if ip_address:
        extra_data['ip_address'] = ip_address
    
    logger.warning(message, extra_data)
