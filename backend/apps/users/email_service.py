import os
import smtplib
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

# Set up logger
logger = get_email_logger()

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
                                <td>${context['amount']:,.2f}</td>
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
                                <td>${context['amount']:,.2f}</td>
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
                                <td>{context['risk_score']}%</td>
                            </tr>
                            <tr>
                                <td>Triggers:</td>
                                <td>{', '.join(context['triggers'])}</td>
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
    """Send HTML email with fallback text content"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = ', '.join(recipient_list)
        
        # Add text version
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        # Add HTML version
        html_part = MIMETextHTML(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if settings.EMAIL_USE_TLS:
                server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        logger.error(f"Error sending HTML email: {e}")
        return False

def send_transaction_notification(user, transaction, status, risk_level="LOW"):
    """Send rich HTML transaction notification email"""
    try:
        logger.info(f"Sending transaction notification to {user.email} for transaction {transaction.id}")
        
        # Prepare context
        context = {
            'user_name': user.first_name or user.email,
            'transaction_id': transaction.id,
            'amount': float(transaction.amount),
            'transaction_type': transaction.transaction_type,
            'status': status.lower(),
            'date': transaction.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'risk_level': risk_level,
            'dashboard_url': f"{settings.SITE_BASE_URL}/client-dashboard"
        }
        
        # Generate HTML content
        html_content = get_html_email_template('transaction_created', context)
        
        # Generate text fallback
        text_content = f"""
        SafeNetAi - Transaction {status.upper()}
        
        Hello {context['user_name']},
        
        Your transaction has been {status.lower()} successfully.
        
        Transaction Details:
        - ID: #{transaction.id}
        - Amount: ${transaction.amount}
        - Type: {transaction.transaction_type}
        - Status: {status.upper()}
        - Date: {context['date']}
        - Risk Level: {risk_level}
        
        View your dashboard: {context['dashboard_url']}
        
        Best regards,
        SafeNetAi Team
        """
        
        # Send email
        success = send_html_email(
            subject=f"SafeNetAi - Transaction {status.title()}",
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
                    "risk_level": risk_level
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

def send_enhanced_fraud_alert_email(profile, fraud_alert):
    """Send enhanced HTML fraud alert email"""
    try:
        logger.info(f"Sending enhanced fraud alert email to {profile.user.email}")
        
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
        
        # Generate HTML content
        html_content = get_html_email_template('fraud_alert', context)
        
        # Generate text fallback
        text_content = f"""
        SafeNetAi - Security Alert
        
        Hello {context['user_name']},
        
        We detected unusual activity on your account.
        
        Transaction Details:
        - ID: #{fraud_alert.transaction.id}
        - Amount: ${fraud_alert.transaction.amount}
        - Type: {fraud_alert.transaction.transaction_type}
        - Risk Level: {fraud_alert.level}
        - Risk Score: {fraud_alert.risk_score}%
        - Triggers: {', '.join(fraud_alert.triggers)}
        
        Please review this transaction and contact support if you don't recognize this activity.
        
        View your dashboard: {context['dashboard_url']}
        
        Best regards,
        SafeNetAi Security Team
        """
        
        # Send email
        success = send_html_email(
            subject="SafeNetAi - Security Alert - Unusual Activity Detected",
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
                    "transaction_id": fraud_alert.transaction.id
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

def send_otp_email(user, otp):
    """Send OTP email to user with comprehensive logging"""
    subject = "SafeNetAi - Email Verification OTP"
    
    message = f"""
    Hello {user.first_name},
    
    Your email verification OTP is: {otp}
    
    This OTP will expire in {settings.EMAIL_TOKEN_TTL_HOURS} hours.
    
    If you didn't request this verification, please ignore this email.
    
    Best regards,
    SafeNetAi Team
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
        
        # Send email
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        if result:
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

def send_fraud_alert_email(profile, fraud_alert):
    """Send fraud alert email to client with logging"""
    # Use the enhanced version
    return send_enhanced_fraud_alert_email(profile, fraud_alert)

def create_otp_for_user(user):
    """Create and send OTP for user with comprehensive logging"""
    try:
        logger.info(f"Creating OTP for user {user.email}")
        
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
        
        # Send email
        success = send_otp_email(user, otp.otp)
        
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

def resend_otp_email(user):
    """Resend OTP email to user"""
    try:
        logger.info(f"Attempting to resend OTP for user {user.email}")
        
        # Check if user has a valid unused OTP
        existing_otp = EmailOTP.objects.filter(user=user, used=False).first()
        
        if existing_otp and existing_otp.expires_at > timezone.now():
            logger.info(f"Resending existing OTP {existing_otp.otp} for user {user.email}")
            success = send_otp_email(user, existing_otp.otp)
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
            return create_otp_for_user(user) is not None
            
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
    """Send security OTP email for high-risk transactions"""
    try:
        subject = f"Security Verification Required - Transaction #{transaction.id}"
        
        # Create email content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                <h2 style="color: #dc3545; margin: 0;">🔒 Security Verification Required</h2>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <p>Hello {user.first_name},</p>
                
                <p>We've detected unusual activity on your account that requires additional verification.</p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0; color: #856404;">Transaction Details:</h3>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Transaction ID:</strong> #{transaction.id}</li>
                        <li><strong>Amount:</strong> {transaction.amount} DZD</li>
                        <li><strong>Type:</strong> {transaction.transaction_type}</li>
                        <li><strong>Risk Score:</strong> {transaction.risk_score}</li>
                    </ul>
                </div>
                
                <p>To complete this transaction, please use the following verification code:</p>
                
                <div style="background-color: #e9ecef; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <h2 style="margin: 0; color: #495057; font-size: 32px; letter-spacing: 5px;">{otp_code}</h2>
                </div>
                
                <p><strong>Important:</strong></p>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>This code expires in 10 minutes</li>
                    <li>Do not share this code with anyone</li>
                    <li>If you didn't initiate this transaction, contact support immediately</li>
                </ul>
                
                <p>If you have any questions or concerns, please contact our support team.</p>
                
                <p>Best regards,<br>The SafeNetAi Team</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d;">
                <p>This is an automated security message. Please do not reply to this email.</p>
            </div>
        </div>
        """
        
        # Send email
        send_html_email(subject, html_content, [user.email])
        
        logger.info(f"Security OTP email sent to {user.email} for transaction {transaction.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send security OTP email: {e}")
        return False
