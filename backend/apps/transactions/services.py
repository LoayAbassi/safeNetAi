"""
Transaction OTP services for SafeNetAi
Handles OTP generation, verification, and cleanup for risky transactions
"""

import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import TransactionOTP
from apps.users.email_service import send_otp_email, send_security_otp_email_async
from apps.utils.logger import get_transactions_logger, log_system_event

logger = get_transactions_logger()

def generate_transaction_otp():
    """Generate a 6-digit OTP for transaction verification"""
    return str(random.randint(100000, 999999))

def create_transaction_otp(transaction, user):
    """Create and send OTP for transaction verification"""
    try:
        logger.info(f"Creating transaction OTP for transaction {transaction.id}, user {user.email}")
        
        # Delete any existing unused OTPs for this transaction
        deleted_count = TransactionOTP.objects.filter(
            transaction=transaction, 
            used=False
        ).delete()[0]
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} existing unused OTPs for transaction {transaction.id}")
        
        # Create new OTP
        otp = TransactionOTP.objects.create(
            transaction=transaction,
            user=user,
            otp=generate_transaction_otp(),
            expires_at=timezone.now() + timedelta(minutes=10)  # 10 minutes expiry
        )
        
        logger.info(f"Created transaction OTP {otp.otp} for transaction {transaction.id}, expires at {otp.expires_at}")
        
<<<<<<< HEAD
        # Send security OTP email asynchronously
        success = send_security_otp_email_async(user, otp.otp, transaction)
=======
        # Send security OTP email
        from apps.users.email_service import send_security_otp_email
        success = send_security_otp_email(user, otp.otp, transaction)
>>>>>>> 3ab812be2863f699c62ef86afe4333f2e0b2a4f3
        
        if success:
            logger.info(f"Transaction OTP created and sent successfully for transaction {transaction.id}")
            log_system_event(
                "Transaction OTP created and sent successfully",
                "transactions",
                "INFO",
                {
                    "user_email": user.email,
                    "user_id": user.id,
                    "transaction_id": transaction.id,
                    "otp_id": otp.id
                }
            )
            return otp
        else:
            logger.error(f"Failed to send transaction OTP email for transaction {transaction.id}, deleting OTP")
            log_system_event(
                "Transaction OTP creation failed - email not sent",
                "transactions",
                "ERROR",
                {
                    "user_email": user.email,
                    "user_id": user.id,
                    "transaction_id": transaction.id,
                    "otp_id": otp.id
                }
            )
            otp.delete()
            return None
            
    except Exception as e:
        logger.error(f"Error creating transaction OTP for transaction {transaction.id}: {e}")
        log_system_event(
            "Error creating transaction OTP",
            "transactions",
            "ERROR",
            {
                "user_email": user.email,
                "user_id": user.id,
                "transaction_id": transaction.id,
                "error": str(e)
            }
        )
        return None

def verify_transaction_otp(transaction_id, otp_code, user):
    """Verify transaction OTP and mark as used"""
    try:
        logger.info(f"Verifying transaction OTP for transaction {transaction_id}, user {user.email}")
        
        # Find the OTP
        transaction_otp = TransactionOTP.objects.filter(
            transaction_id=transaction_id,
            user=user,
            used=False
        ).first()
        
        if not transaction_otp:
            logger.warning(f"No valid OTP found for transaction {transaction_id}, user {user.email}")
            return {
                'success': False,
                'error': 'No valid OTP found for this transaction'
            }
        
        # Check if OTP is expired
        if transaction_otp.is_expired():
            logger.warning(f"Transaction OTP expired for transaction {transaction_id}")
            transaction_otp.mark_used()  # Mark as used to prevent reuse
            return {
                'success': False,
                'error': 'OTP has expired'
            }
        
        # Check if too many attempts
        if transaction_otp.attempts >= 3:
            logger.warning(f"Too many OTP attempts for transaction {transaction_id}")
            transaction_otp.mark_used()
            return {
                'success': False,
                'error': 'Too many failed attempts'
            }
        
        # Verify OTP
        if transaction_otp.otp != otp_code:
            transaction_otp.increment_attempts()
            logger.warning(f"Invalid OTP attempt for transaction {transaction_id}, attempts: {transaction_otp.attempts}")
            return {
                'success': False,
                'error': 'Invalid OTP code'
            }
        
        # OTP is valid - mark as used
        transaction_otp.mark_used()
        logger.info(f"Transaction OTP verified successfully for transaction {transaction_id}")
        
        log_system_event(
            "Transaction OTP verified successfully",
            "transactions",
            "INFO",
            {
                "user_email": user.email,
                "user_id": user.id,
                "transaction_id": transaction_id,
                "otp_id": transaction_otp.id
            }
        )
        
        return {
            'success': True,
            'message': 'OTP verified successfully'
        }
        
    except Exception as e:
        logger.error(f"Error verifying transaction OTP for transaction {transaction_id}: {e}")
        log_system_event(
            "Error verifying transaction OTP",
            "transactions",
            "ERROR",
            {
                "user_email": user.email,
                "user_id": user.id,
                "transaction_id": transaction_id,
                "error": str(e)
            }
        )
        return {
            'success': False,
            'error': 'Verification failed'
        }

def cleanup_expired_otps():
    """Clean up expired transaction OTPs"""
    try:
        expired_otps = TransactionOTP.objects.filter(
            expires_at__lt=timezone.now(),
            used=False
        )
        
        count = expired_otps.count()
        expired_otps.delete()
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired transaction OTPs")
            log_system_event(
                "Expired transaction OTPs cleaned up",
                "transactions",
                "INFO",
                {"expired_count": count}
            )
        
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired transaction OTPs: {e}")
        return 0

def resend_transaction_otp(transaction_id, user):
    """Resend transaction OTP"""
    try:
        logger.info(f"Attempting to resend transaction OTP for transaction {transaction_id}, user {user.email}")
        
        # Check if user has a valid unused OTP for this transaction
        existing_otp = TransactionOTP.objects.filter(
            transaction_id=transaction_id,
            user=user,
            used=False
        ).first()
        
        if existing_otp and not existing_otp.is_expired():
            logger.info(f"Resending existing transaction OTP {existing_otp.otp} for transaction {transaction_id}")
            # Get transaction for email template
<<<<<<< HEAD
            from apps.users.email_service import send_security_otp_email_async
            success = send_security_otp_email_async(user, existing_otp.otp, existing_otp.transaction)
=======
            from apps.users.email_service import send_security_otp_email
            success = send_security_otp_email(user, existing_otp.otp, existing_otp.transaction)
>>>>>>> 3ab812be2863f699c62ef86afe4333f2e0b2a4f3
            if success:
                log_system_event(
                    "Transaction OTP resent successfully",
                    "transactions",
                    "INFO",
                    {
                        "user_email": user.email,
                        "user_id": user.id,
                        "transaction_id": transaction_id,
                        "otp_id": existing_otp.id
                    }
                )
            return success
        else:
            logger.info(f"No valid transaction OTP found for transaction {transaction_id}, creating new one")
            # Get the transaction
            from .models import Transaction
            try:
                transaction = Transaction.objects.get(id=transaction_id)
                return create_transaction_otp(transaction, user) is not None
            except Transaction.DoesNotExist:
<<<<<<< HEAD
                logger.error(f"Transaction {transaction_id} not found when trying to resend OTP")
                return False
                
=======
                logger.error(f"Transaction {transaction_id} not found")
                return False
            
>>>>>>> 3ab812be2863f699c62ef86afe4333f2e0b2a4f3
    except Exception as e:
        logger.error(f"Error resending transaction OTP for transaction {transaction_id}: {e}")
        log_system_event(
            "Error resending transaction OTP",
            "transactions",
            "ERROR",
            {
                "user_email": user.email,
                "user_id": user.id,
                "transaction_id": transaction_id,
                "error": str(e)
            }
        )
        return False
