import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText as MIMETextHTML
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP
from apps.utils.logger import get_email_logger, log_system_event
from .email_templates import (
    get_otp_email_template,
    get_security_otp_email_template,
    get_transaction_notification_template,
    get_fraud_alert_template
)
# Import SendGrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Set up logger
logger = get_email_logger()

# Default language
DEFAULT_LANGUAGE = 'en'

# Remove the global USER_LANGUAGES dictionary since we now store language in the database

def get_user_language(user):
    """Get user's preferred language from the database"""
    return getattr(user, 'language', DEFAULT_LANGUAGE) if user else DEFAULT_LANGUAGE

def generate_otp():
    """Generate a 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))

def get_html_email_template(template_name, context):
    """Get HTML email template with branding"""
    templates = {
        'transaction_created': f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SafeNetAi - Transaction Created</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 30px; }}
                .transaction-details {{ background-color: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .transaction-details table {{ width: 100%; border-collapse: collapse; }}
                .transaction-details td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
                .transaction-details td:first-child {{ font-weight: bold; color: #4a5568; }}
                .status-approved {{ color: #38a169; font-weight: bold; }}
                .status-pending {{ color: #d69e2e; font-weight: bold; }}
                .status-rejected {{ color: #e53e3e; font-weight: bold; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ background-color: #2d3748; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                .logo {{ width: 40px; height: 40px; background-color: white; border-radius: 50%; display: inline-block; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🛡️</div>
                    <h1>SafeNetAi</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Transaction Notification</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #2d3748; margin-bottom: 20px;">Transaction {context['status'].title()}</h2>
                    
                    <p>Hello {context['user_name']},</p>
                    
                    <p>Your transaction has been <strong>{context['status']}</strong> successfully.</p>
                    
                    <div class="transaction-details">
                        <table>
                            <tr>
                                <td>Transaction ID:</td>
                                <td>#{context['transaction_id']}</td>
                            </tr>
                            <tr>
                                <td>Amount:</td>
                                <td>{context['amount']:,.2f} DZD</td>
                            </tr>
                            <tr>
                                <td>Type:</td>
                                <td>{context['transaction_type'].title()}</td>
                            </tr>
                            <tr>
                                <td>Status:</td>
                                <td class="status-{context['status']}">{context['status'].upper()}</td>
                            </tr>
                            <tr>
                                <td>Date:</td>
                                <td>{context['date']}</td>
                            </tr>
                            <tr>
                                <td>Risk Level:</td>
                                <td>{context['risk_level']}</td>
                            </tr>
                            <tr>
                                <td>Risk Score:</td>
                                <td>{context.get('risk_score', 0)}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <a href="{context['dashboard_url']}" class="cta-button">View Dashboard</a>
                    
                    <p style="color: #718096; font-size: 14px; margin-top: 30px;">
                        If you have any questions, please contact our support team.
                    </p>
                </div>
                
                <div class="footer">
                    <p>&copy; 2025 SafeNetAi. All rights reserved.</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """,
        
        'fraud_alert': f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SafeNetAi - Security Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 30px; }}
                .alert-box {{ background-color: #fed7d7; border: 2px solid #e53e3e; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .transaction-details {{ background-color: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .transaction-details table {{ width: 100%; border-collapse: collapse; }}
                .transaction-details td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
                .transaction-details td:first-child {{ font-weight: bold; color: #4a5568; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ background-color: #2d3748; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                .logo {{ width: 40px; height: 40px; background-color: white; border-radius: 50%; display: inline-block; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🚨</div>
                    <h1>SafeNetAi Security Alert</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Unusual Activity Detected</p>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <h3 style="color: #c53030; margin-top: 0;">⚠️ Security Alert</h3>
                        <p style="color: #c53030; margin-bottom: 0;">We detected unusual activity on your account that requires your attention.</p>
                    </div>
                    
                    <p>Hello {context['user_name']},</p>
                    
                    <p>Our AI-powered security system has flagged a transaction on your account as potentially suspicious.</p>
                    
                    <div class="transaction-details">
                        <table>
                            <tr>
                                <td>Transaction ID:</td>
                                <td>#{context['transaction_id']}</td>
                            </tr>
                            <tr>
                                <td>Amount:</td>
                                <td>{context['amount']:,.2f} DZD</td>
                            </tr>
                            <tr>
                                <td>Type:</td>
                                <td>{context['transaction_type'].title()}</td>
                            </tr>
                            <tr>
                                <td>Risk Level:</td>
                                <td style="color: #e53e3e; font-weight: bold;">{context['risk_level'].upper()}</td>
                            </tr>
                            <tr>
                                <td>Risk Score:</td>
                                <td>{context.get('risk_score', 0)}%</td>
                            </tr>
                            <tr>
                                <td>Triggers:</td>
                                <td>{', '.join(context.get('triggers', []))}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <a href="{context['dashboard_url']}" class="cta-button">Review Transaction</a>
                    
                    <p style="color: #718096; font-size: 14px; margin-top: 30px;">
                        If you don't recognize this transaction, please contact our security team immediately.
                    </p>
                </div>
                
                <div class="footer">
                    <p>&copy; 2025 SafeNetAi. All rights reserved.</p>
                    <p>This is an automated security alert, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
    }
    
    return templates.get(template_name, '')

def send_html_email(subject, html_content, recipient_list, text_content=None):
    """Send HTML email with fallback text content using SendGrid API"""
    try:
        # Create SendGrid message
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=recipient_list,  # SendGrid API can handle a list of recipients
            subject=subject,
            html_content=html_content
        )
        
        # Add plain text content if provided
        if text_content:
            message.plain_text_content = text_content
        
        # Send email using SendGrid API
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        # Log successful sending
        logger.info(f"Email sent successfully via SendGrid API to {', '.join(recipient_list)} with status code {response.status_code}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending HTML email via SendGrid API: {e}")
        return False

def send_html_email_async(subject, html_content, recipient_list, text_content=None):
    """Send HTML email asynchronously to prevent blocking API responses"""
    def send_email():
        try:
            send_html_email(subject, html_content, recipient_list, text_content)
        except Exception as e:
            logger.error(f"Error in async email sending: {e}")
    
    # Start email sending in a separate thread
    email_thread = threading.Thread(target=send_email)
    email_thread.daemon = True  # Thread will die when main process dies
    email_thread.start()
    
    # Return immediately without waiting for email to be sent
    return True

def send_transaction_notification(user, transaction, status, risk_level="LOW"):
    """Send rich HTML transaction notification email"""
    try:
        logger.info(f"Sending transaction notification to {user.email} for transaction {transaction.id} using language: {get_user_language(user)}")
        
        # Prepare context
        context = {
            'user_name': user.first_name or user.email,
            'transaction_id': transaction.id,
            'amount': float(transaction.amount),
            'transaction_type': transaction.transaction_type,
            'status': status.lower(),
            'date': transaction.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'risk_level': risk_level,
            'risk_score': getattr(transaction, 'risk_score', 0),  # Add risk_score with default
            'dashboard_url': f"{settings.SITE_BASE_URL}/client-dashboard"
        }
        
        # Get user's preferred language
        user_language = get_user_language(user)
        
        # Get template based on language
        template = get_transaction_notification_template(user_language)
        subject = template['subject'].format(status=status.title())
        
        # Generate HTML content
        html_content = get_html_email_template('transaction_created', context)
        
        # Generate text fallback
        text_content = f"""
        SafeNetAi - Transaction {status.upper()}
        
        Hello {context['user_name']},
        
        Your transaction has been {status.lower()} successfully.
        
        Transaction Details:
        - ID: #{transaction.id}
        - Amount: {transaction.amount} DZD
        - Type: {transaction.transaction_type}
        - Status: {status.upper()}
        - Date: {context['date']}
        - Risk Level: {risk_level}
        - Risk Score: {context['risk_score']}
        
        View your dashboard: {context['dashboard_url']}
        
        Best regards,
        SafeNetAi Team
        """
        
        # Send email asynchronously
        success = send_html_email_async(
            subject=subject,
            html_content=html_content,
            recipient_list=[user.email],
            text_content=text_content
        )
        
        if success:
            logger.info(f"Transaction notification sent successfully to {user.email}")
            log_system_event(
                "Transaction notification sent successfully",
                "email_service",
                "INFO",
                {
                    "user_email": user.email,
                    "user_id": user.id,
                    "transaction_id": transaction.id,
                    "status": status,
                    "risk_level": risk_level,
                    "risk_score": context['risk_score']
                }
            )
            return True
        else:
            logger.error(f"Failed to send transaction notification to {user.email}")
            log_system_event(
                "Transaction notification failed to send",
                "email_service",
                "ERROR",
                {
                    "user_email": user.email,
                    "user_id": user.id,
                    "transaction_id": transaction.id,
                    "status": status,
                    "risk_level": risk_level
                }
            )
            return False
            
    except Exception as e:
        logger.error(f"Error sending transaction notification: {e}")
        log_system_event(
            "Error sending transaction notification",
            "email_service",
            "ERROR",
            {
                "user_email": user.email,
                "user_id": user.id,
                "transaction_id": transaction.id,
                "error": str(e)
            }
        )
        return False

def send_transaction_notification_async(user, transaction, status, risk_level="LOW"):
    """Send transaction notification email asynchronously to prevent blocking API responses"""
    def send_email():
        try:
            send_transaction_notification(user, transaction, status, risk_level)
        except Exception as e:
            logger.error(f"Error in async transaction notification sending: {e}")
    
    # Start email sending in a separate thread
    email_thread = threading.Thread(target=send_email)
    email_thread.daemon = True  # Thread will die when main process dies
    email_thread.start()
    
    # Return immediately without waiting for email to be sent
    return True

def send_enhanced_fraud_alert_email(profile, fraud_alert):
    """Send enhanced HTML fraud alert email"""
    try:
        logger.info(f"Sending enhanced fraud alert email to {profile.user.email} using language: {get_user_language(profile.user)}")
        
        # Prepare context
        context = {
            'user_name': profile.first_name or profile.user.email,
            'transaction_id': fraud_alert.transaction.id,
            'amount': float(fraud_alert.transaction.amount),
            'transaction_type': fraud_alert.transaction.transaction_type,
            'risk_level': fraud_alert.level,
            'risk_score': fraud_alert.risk_score,
            'triggers': fraud_alert.triggers,
            'dashboard_url': f"{settings.SITE_BASE_URL}/client-dashboard"
        }
        
        # Get user's preferred language
        user_language = get_user_language(profile.user)
        
        # Get template based on language
        template = get_fraud_alert_template(user_language)
        subject = template['subject']
        
        # Generate HTML content
        html_content = get_html_email_template('fraud_alert', context)
        
        # Generate text fallback
        text_content = f"""
        SafeNetAi - Security Alert
        
        Hello {context['user_name']},
        
        We detected unusual activity on your account that requires your attention.
        
        Transaction Details:
        - ID: #{fraud_alert.transaction.id}
        - Amount: {fraud_alert.transaction.amount} DZD
        - Type: {fraud_alert.transaction.transaction_type}
        - Risk Level: {fraud_alert.level}
        - Risk Score: {fraud_alert.risk_score}%
        - Triggers: {', '.join(fraud_alert.triggers)}
        
        Review your dashboard: {context['dashboard_url']}
        
        Best regards,
        SafeNetAi Security Team
        """
        
        # Send email asynchronously
        success = send_html_email_async(
            subject=subject,
            html_content=html_content,
            recipient_list=[profile.user.email],
            text_content=text_content
        )
        
        if success:
            logger.info(f"Enhanced fraud alert email sent successfully to {profile.user.email}")
            log_system_event(
                "Enhanced fraud alert email sent successfully",
                "email_service",
                "INFO",
                {
                    "user_email": profile.user.email,
                    "user_id": profile.user.id,
                    "transaction_id": fraud_alert.transaction.id,
                    "risk_level": fraud_alert.level,
                    "risk_score": fraud_alert.risk_score
                }
            )
            return True
        else:
            logger.error(f"Failed to send enhanced fraud alert email to {profile.user.email}")
            log_system_event(
                "Enhanced fraud alert email failed to send",
                "email_service",
                "ERROR",
                {
                    "user_email": profile.user.email,
                    "user_id": profile.user.id,
                    "transaction_id": fraud_alert.transaction.id,
                    "risk_level": fraud_alert.level,
                    "risk_score": fraud_alert.risk_score
                }
            )
            return False
            
    except Exception as e:
        logger.error(f"Error sending enhanced fraud alert email: {e}")
        log_system_event(
            "Error sending enhanced fraud alert email",
            "email_service",
            "ERROR",
            {
                "user_email": profile.user.email,
                "user_id": profile.user.id,
                "transaction_id": fraud_alert.transaction.id,
                "error": str(e)
            }
        )
        return False

def send_enhanced_fraud_alert_email_async(profile, fraud_alert):
    """Send enhanced fraud alert email asynchronously to prevent blocking API responses"""
    def send_email():
        try:
            send_enhanced_fraud_alert_email(profile, fraud_alert)
        except Exception as e:
            logger.error(f"Error in async fraud alert email sending: {e}")
    
    # Start email sending in a separate thread
    email_thread = threading.Thread(target=send_email)
    email_thread.daemon = True  # Thread will die when main process dies
    email_thread.start()
    
    # Return immediately without waiting for email to be sent
    return True

def send_otp_email(user, otp, language='en'):
    """Send elegant HTML OTP email to user with comprehensive logging"""
    # Log the language being used for this email
    logger.info(f"Sending OTP email to {user.email} using language: {language}")
    
    template = get_otp_email_template(language)
    subject = template['subject']
    
    # Create elegant HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{template['title']}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 600; }}
            .header p {{ color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 16px; }}
            .content {{ padding: 40px 30px; text-align: center; }}
            .otp-container {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; padding: 30px; margin: 30px 0; }}
            .otp-code {{ font-family: 'Courier New', monospace; font-size: 36px; font-weight: bold; color: white; letter-spacing: 8px; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }}
            .otp-label {{ color: rgba(255,255,255,0.9); font-size: 14px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }}
            .instructions {{ background-color: #f8fafc; border-radius: 8px; padding: 20px; margin: 30px 0; text-align: left; }}
            .instructions h3 {{ color: #2d3748; margin-top: 0; }}
            .instructions ul {{ color: #4a5568; margin: 15px 0; padding-left: 20px; }}
            .security-note {{ background-color: #fed7d7; border-left: 4px solid #e53e3e; padding: 15px; margin: 20px 0; text-align: left; }}
            .footer {{ background-color: #2d3748; color: white; padding: 30px; text-align: center; font-size: 14px; }}
            .footer p {{ margin: 5px 0; }}
            .logo {{ width: 50px; height: 50px; background-color: white; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 15px; font-size: 24px; }}
            .timer {{ background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 15px; margin: 20px 0; }}
            .timer strong {{ color: #856404; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🔐</div>
                <h1>{template['title']}</h1>
                <p>{template['greeting'].format(user_name=user.first_name or 'User')}</p>
            </div>
            
            <div class="content">
                <h2 style="color: #2d3748; margin-bottom: 20px;">{template['greeting'].format(user_name=user.first_name or 'User')}!</h2>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                    {template['message']}
                </p>
                
                <div class="otp-container">
                    <div class="otp-label">{template['code_label']}</div>
                    <div class="otp-code">{otp}</div>
                </div>
                
                <div class="timer">
                    <strong>⏰ {template['expires_in'].format(hours=settings.EMAIL_TOKEN_TTL_HOURS)}</strong>
                </div>
                
                <div class="instructions">
                    <h3>{template['instructions_title']}</h3>
                    <ul>
                        <li>{template['instructions'][0]}</li>
                        <li>{template['instructions'][1]}</li>
                        <li>{template['instructions'][2]}</li>
                        <li>{template['instructions'][3]}</li>
                    </ul>
                </div>
                
                <div class="security-note">
                    <strong>🔒 {template['security_notice']}</strong>
                </div>
                
                <p style="color: #718096; font-size: 14px; margin-top: 40px;">
                    {template['support']}
                </p>
            </div>
            
            <div class="footer">
                <p><strong>&copy; 2025 SafeNetAi. All rights reserved.</strong></p>
                <p>{template['footer']}</p>
                <p style="font-size: 12px; margin-top: 15px; opacity: 0.8;">{template['auto_message']}</p>
            </div>
        </div>
    </body>
    """
    
    # Text fallback
    text_content = f"""
    {template['title']}
    
    {template['greeting'].format(user_name=user.first_name or 'User')},
    
    {template['code_label']}: {otp}
    
    {template['expires_in'].format(hours=settings.EMAIL_TOKEN_TTL_HOURS)}.
    
    {template['security_notice']}.
    
    {template['footer']}
    """
    
    try:
        logger.info(f"Attempting to send OTP email to {user.email}")
        logger.info(f"Email settings - Backend: {settings.EMAIL_BACKEND}, Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}, User: {settings.EMAIL_HOST_USER}, TLS: {settings.EMAIL_USE_TLS}, SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        
        # Check if email settings are configured
        if not settings.EMAIL_HOST_USER:
            logger.error("EMAIL_HOST_USER not configured")
            return False
            
        if not settings.EMAIL_HOST_PASSWORD:
            logger.error("EMAIL_HOST_PASSWORD not configured")
            return False
            
        if not settings.EMAIL_HOST:
            logger.error("EMAIL_HOST not configured")
            return False
        
        # Send HTML email asynchronously
        success = send_html_email_async(
            subject=subject,
            html_content=html_content,
            recipient_list=[user.email],
            text_content=text_content
        )
        
        if success:
            logger.info(f"OTP email sent successfully to {user.email}. OTP: {otp}")
            log_system_event(
                "OTP email sent successfully",
                "email_service",
                "INFO",
                {"user_email": user.email, "user_id": user.id}
            )
            return True
        else:
            logger.error(f"Failed to send OTP email to {user.email}")
            log_system_event(
                "OTP email failed to send",
                "email_service",
                "ERROR",
                {"user_email": user.email, "user_id": user.id}
            )
            return False
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        log_system_event(
            "SMTP authentication failed",
            "email_service",
            "ERROR",
            {"user_email": user.email, "user_id": user.id, "error": str(e)}
        )
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        log_system_event(
            "SMTP error occurred",
            "email_service",
            "ERROR",
            {"user_email": user.email, "user_id": user.id, "error": str(e)}
        )
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending OTP email: {e}")
        log_system_event(
            "Unexpected error in email service",
            "email_service",
            "ERROR",
            {"user_email": user.email, "user_id": user.id, "error": str(e)}
        )
        return False

def send_otp_email_async(user, otp, language='en'):
    """Send OTP email asynchronously to prevent blocking API responses"""
    def send_email():
        try:
            send_otp_email(user, otp, language)
        except Exception as e:
            logger.error(f"Error in async OTP email sending: {e}")
    
    # Start email sending in a separate thread
    email_thread = threading.Thread(target=send_email)
    email_thread.daemon = True  # Thread will die when main process dies
    email_thread.start()
    
    # Return immediately without waiting for email to be sent
    return True

def send_fraud_alert_email(profile, fraud_alert):
    """Send fraud alert email to client with logging"""
    # Use the enhanced version asynchronously
    return send_enhanced_fraud_alert_email_async(profile, fraud_alert)

def create_otp_for_user(user, language=None):
    """Create and send OTP for user with comprehensive logging"""
    try:
        logger.info(f"Creating OTP for user {user.email}")
        
        # Use provided language or get from user preference
        user_language = language or get_user_language(user)
        
        # Delete any existing unused OTPs for this user
        deleted_count = EmailOTP.objects.filter(user=user, used=False).delete()[0]
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} existing unused OTPs for user {user.email}")

        # Create new OTP
        otp = EmailOTP.objects.create(
            user=user,
            otp=generate_otp(),
            expires_at=timezone.now() + timedelta(hours=settings.EMAIL_TOKEN_TTL_HOURS)
        )

        logger.info(f"Created OTP {otp.otp} for user {user.email}, expires at {otp.expires_at}")

        # Send email asynchronously
        success = send_otp_email_async(user, otp.otp, user_language)

        if success:
            logger.info(f"OTP created and sent successfully for user {user.email}")
            log_system_event(
                "OTP created and sent successfully",
                "email_service",
                "INFO",
                {"user_email": user.email, "user_id": user.id, "otp_id": otp.id}
            )
            return otp
        else:
            logger.error(f"Failed to send OTP email for user {user.email}, deleting OTP")
            log_system_event(
                "OTP creation failed - email not sent",
                "email_service",
                "ERROR",
                {"user_email": user.email, "user_id": user.id, "otp_id": otp.id}
            )
            otp.delete()
            return None
            
    except Exception as e:
        logger.error(f"Error creating OTP for user {user.email}: {e}")
        log_system_event(
            "Error creating OTP",
            "email_service",
            "ERROR",
            {"user_email": user.email, "user_id": user.id, "error": str(e)}
        )
        return None

def resend_otp_email(user, language=None):
    """Resend OTP email to user"""
    try:
        logger.info(f"Attempting to resend OTP for user {user.email}")
        
        # Use provided language or get from user preference
        user_language = language or get_user_language(user)
        
        # Check if user has a valid unused OTP
        existing_otp = EmailOTP.objects.filter(user=user, used=False).first()
        
        if existing_otp and existing_otp.expires_at > timezone.now():
            logger.info(f"Resending existing OTP {existing_otp.otp} for user {user.email}")
            success = send_otp_email_async(user, existing_otp.otp, user_language)
            if success:
                log_system_event(
                    "OTP resent successfully",
                    "email_service",
                    "INFO",
                    {"user_email": user.email, "user_id": user.id, "otp_id": existing_otp.id}
                )
            return success
        else:
            logger.info(f"No valid OTP found for user {user.email}, creating new one")
            return create_otp_for_user(user, user_language) is not None
            
    except Exception as e:
        logger.error(f"Error resending OTP for user {user.email}: {e}")
        log_system_event(
            "Error resending OTP",
            "email_service",
            "ERROR",
            {"user_email": user.email, "user_id": user.id, "error": str(e)}
        )
        return False

def resend_otp(user, language=None):
    """Resend OTP to user with comprehensive logging"""
    try:
        logger.info(f"Resending OTP to user {user.email}")
        
        # Use provided language or get from user preference
        user_language = language or get_user_language(user)
        
        # Check if user has a valid unused OTP
        existing_otp = EmailOTP.objects.filter(user=user, used=False).first()
        
        if existing_otp and existing_otp.expires_at > timezone.now():
            logger.info(f"Resending existing OTP {existing_otp.otp} for user {user.email}")
            success = send_otp_email_async(user, existing_otp.otp, user_language)
            if success:
                log_system_event(
                    "OTP resent successfully",
                    "email_service",
                    "INFO",
                    {"user_email": user.email, "user_id": user.id, "otp_id": existing_otp.id}
                )
            return success
        else:
            logger.info(f"No valid OTP found for user {user.email}, creating new one")
            return create_otp_for_user(user, user_language) is not None
            
    except Exception as e:
        logger.error(f"Error resending OTP for user {user.email}: {e}")
        log_system_event(
            "Error resending OTP",
            "email_service",
            "ERROR",
            {"user_email": user.email, "user_id": user.id, "error": str(e)}
        )
        return False

def send_security_otp_email(user, otp_code, transaction):
    """Send elegant security OTP email for high-risk transactions"""
    try:
        # Get user's preferred language
        user_language = get_user_language(user)
        logger.info(f"Sending security OTP email to {user.email} using language: {user_language}")
        
        template = get_security_otp_email_template(user_language)
        subject = template['subject'].format(transaction_id=transaction.id)
        
        # Create elegant HTML content for transaction OTP
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SafeNetAi - Security Verification</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%); padding: 40px 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 600; }}
                .header p {{ color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 16px; }}
                .content {{ padding: 40px 30px; }}
                .alert-banner {{ background-color: #fed7d7; border: 2px solid #e53e3e; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center; }}
                .alert-banner h3 {{ color: #c53030; margin: 0 0 10px 0; }}
                .transaction-details {{ background-color: #f8fafc; border-radius: 8px; padding: 25px; margin: 25px 0; }}
                .transaction-details table {{ width: 100%; border-collapse: collapse; }}
                .transaction-details td {{ padding: 12px 0; border-bottom: 1px solid #e2e8f0; }}
                .transaction-details td:first-child {{ font-weight: 600; color: #2d3748; width: 40%; }}
                .transaction-details td:last-child {{ color: #4a5568; }}
                .otp-container {{ background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%); border-radius: 12px; padding: 30px; margin: 30px 0; text-align: center; }}
                .otp-label {{ color: rgba(255,255,255,0.9); font-size: 14px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }}
                .otp-code {{ font-family: 'Courier New', monospace; font-size: 42px; font-weight: bold; color: white; letter-spacing: 10px; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }}
                .instructions {{ background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 25px 0; }}
                .instructions h4 {{ color: #856404; margin-top: 0; }}
                .instructions ol {{ color: #856404; margin: 15px 0; padding-left: 20px; }}
                .security-warning {{ background-color: #f7fafc; border-left: 4px solid #4299e1; padding: 20px; margin: 25px 0; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: 600; }}
                .footer {{ background-color: #2d3748; color: white; padding: 30px; text-align: center; font-size: 14px; }}
                .footer p {{ margin: 5px 0; }}
                .logo {{ width: 50px; height: 50px; background-color: white; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 15px; font-size: 24px; }}
                .timer {{ background-color: #fed7d7; border: 1px solid #e53e3e; border-radius: 6px; padding: 15px; margin: 20px 0; text-align: center; }}
                .timer strong {{ color: #c53030; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔒</div>
                    <h1>Security Verification Required</h1>
                    <p>Protect your SafeNetAi account</p>
                </div>
                
                <div class="content">
                    <div class="alert-banner">
                        <h3>⚠️ Unusual Activity Detected</h3>
                        <p style="color: #c53030; margin: 0;">We've detected suspicious activity and need to verify this transaction.</p>
                    </div>
                    
                    <p style="font-size: 16px; color: #2d3748; margin-bottom: 25px;">
                        Hello <strong>{user.first_name or 'User'}</strong>,
                    </p>
                    
                    <p style="color: #4a5568; line-height: 1.6; margin-bottom: 25px;">
                        Our AI-powered security system has flagged a transaction on your account that requires additional verification before processing.
                    </p>
                    
                    <div class="transaction-details">
                        <h4 style="color: #2d3748; margin-top: 0; margin-bottom: 20px;">💳 Transaction Details</h4>
                        <table>
                            <tr>
                                <td>Transaction ID:</td>
                                <td><strong>#{transaction.id}</strong></td>
                            </tr>
                            <tr>
                                <td>Amount:</td>
                                <td><strong>{transaction.amount:,.2f} DZD</strong></td>
                            </tr>
                            <tr>
                                <td>Type:</td>
                                <td><strong>{transaction.transaction_type.title()}</strong></td>
                            </tr>
                            <tr>
                                <td>Risk Score:</td>
                                <td><strong style="color: #e53e3e;">{transaction.risk_score}/100</strong></td>
                            </tr>
                            <tr>
                                <td>Status:</td>
                                <td><strong style="color: #d69e2e;">Pending Verification</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <div class="otp-container">
                        <div class="otp-label">Your Security Code</div>
                        <div class="otp-code">{otp_code}</div>
                    </div>
                    
                    <div class="timer">
                        <strong>⏰ This code expires in 10 minutes</strong>
                    </div>
                    
                    <div class="instructions">
                        <h4>Complete your transaction:</h4>
                        <ol>
                            <li>Copy the 6-digit security code above</li>
                            <li>Return to your SafeNetAi transaction page</li>
                            <li>Enter the code when prompted</li>
                            <li>Click "Verify" to complete your transaction</li>
                        </ol>
                    </div>
                    
                    <div class="security-warning">
                        <strong>🔒 Security Notice:</strong> If you didn't initiate this transaction, please contact our security team immediately at security@safenetai.com or call +213-XXX-XXXX.
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{settings.SITE_BASE_URL}/client-dashboard" class="cta-button">
                            Access Your Dashboard
                        </a>
                    </div>
                    
                    <p style="color: #718096; font-size: 14px; margin-top: 40px; text-align: center;">
                        Need assistance? Our security team is available 24/7 to help protect your account.
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>&copy; 2025 SafeNetAi Security Team</strong></p>
                    <p>Advanced AI-Powered Financial Protection</p>
                    <p style="font-size: 12px; margin-top: 15px; opacity: 0.8;">This security alert was automatically generated. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text fallback
        text_content = f"""
        SafeNetAi - Security Verification Required
        
        Hello {user.first_name or 'User'},
        
        We've detected unusual activity on your account that requires verification.
        
        Transaction Details:
        - ID: #{transaction.id}
        - Amount: {transaction.amount:,.2f} DZD
        - Type: {transaction.transaction_type}
        - Risk Score: {transaction.risk_score}/100
        
        Your Security Code: {otp_code}
        
        This code expires in 10 minutes.
        
        If you didn't initiate this transaction, contact security@safenetai.com immediately.
        
        Best regards,
        SafeNetAi Security Team
        """
        
        # Send HTML email
        success = send_html_email(
            subject=subject,
            html_content=html_content,
            recipient_list=[user.email],
            text_content=text_content
        )
        
        if success:
            logger.info(f"Security OTP email sent successfully to {user.email} for transaction {transaction.id}")
            log_system_event(
                "Security OTP email sent successfully",
                "email_service",
                "INFO",
                {
                    "user_email": user.email,
                    "user_id": user.id,
                    "transaction_id": transaction.id,
                    "otp_code": otp_code
                }
            )
            return True
        else:
            logger.error(f"Failed to send security OTP email to {user.email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending security OTP email: {e}")
        log_system_event(
            "Error sending security OTP email",
            "email_service",
            "ERROR",
            {
                "user_email": user.email,
                "user_id": user.id,
                "transaction_id": transaction.id,
                "error": str(e)
            }
        )
        return False

def send_security_otp_email_async(user, otp_code, transaction):
    """Send security OTP email asynchronously to prevent blocking API responses"""
    def send_email():
        try:
            send_security_otp_email(user, otp_code, transaction)
        except Exception as e:
            logger.error(f"Error in async security OTP email sending: {e}")
    
    # Start email sending in a separate thread
    email_thread = threading.Thread(target=send_email)
    email_thread.daemon = True  # Thread will die when main process dies
    email_thread.start()
    
    # Return immediately without waiting for email to be sent
    return True
