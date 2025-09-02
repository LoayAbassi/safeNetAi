from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .serializers import (
    TransactionSerializer, CreateTransactionSerializer, AdminTransactionSerializer,
    FraudAlertSerializer, AdminFraudAlertSerializer
)
from .models import Transaction, FraudAlert
from apps.risk.models import ClientProfile
from apps.risk.engine import RiskEngine
from apps.risk.ml import FraudMLModel
from apps.users.email_service import send_fraud_alert_email, send_transaction_notification
from apps.transactions.services import create_transaction_otp, verify_transaction_otp, resend_transaction_otp
from apps.utils.logger import get_transactions_logger, log_transaction, log_system_event

# Set up logger
logger = get_transactions_logger()

class TransactionViewSet(viewsets.ModelViewSet):
    """Transaction viewset for clients"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            client_profile = ClientProfile.objects.get(user=self.request.user)
            return Transaction.objects.filter(client=client_profile)
        except ClientProfile.DoesNotExist:
            return Transaction.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransactionSerializer
        return TransactionSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create transaction with fraud detection and balance updates"""
        logger.info(f"Creating transaction for user {request.user.email}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get client profile
                client_profile = ClientProfile.objects.get(user=request.user)
                logger.info(f"Client profile found: {client_profile.full_name}")
                
                # Validate funds for transfer
                transaction_type = serializer.validated_data.get('transaction_type')
                amount = serializer.validated_data.get('amount')
                
                if transaction_type == 'transfer':
                    if client_profile.balance < amount:
                        logger.warning(f"Insufficient funds for user {request.user.email}. Balance: {client_profile.balance}, Required: {amount}")
                        log_transaction(
                            transaction_id=0,  # Not created yet
                            amount=amount,
                            transaction_type=transaction_type,
                            user_id=request.user.id,
                            status="REJECTED_INSUFFICIENT_FUNDS"
                        )
                        return Response({
                            'error': 'Insufficient funds'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create transaction
                transaction_obj = serializer.save(client=client_profile)
                logger.info(f"Transaction created: ID {transaction_obj.id}, Amount: {amount}, Type: {transaction_type}")
                
                # Run fraud detection
                risk_engine = RiskEngine()
                risk_score, triggers, requires_otp, decision = risk_engine.calculate_risk_score(transaction_obj)
                logger.info(f"Risk assessment: Score={risk_score}, Triggers={triggers}, Requires OTP={requires_otp}, Decision={decision}")
                
                # Add ML score if available
                ml_model = FraudMLModel()
                ml_score = ml_model.predict(transaction_obj)
                ml_contribution = int(ml_score * 40)  # ML contributes up to 40 points
                risk_score += ml_contribution
                logger.info(f"ML score: {ml_score}, Contribution: {ml_contribution}, Final risk score: {risk_score}")
                
                # Update transaction with risk score
                transaction_obj.risk_score = risk_score
                transaction_obj.save()
                
                # Log comprehensive transaction details
                logger.info(f"Transaction details: ID={transaction_obj.id}, Client={client_profile.full_name}, "
                          f"Type={transaction_type}, Amount={amount} DZD, Risk Score={risk_score}, "
                          f"Decision={decision}, Triggers={triggers}")
                
                # Log transaction using structured logging
                log_transaction(
                    transaction_id=transaction_obj.id,
                    amount=amount,
                    transaction_type=transaction_type,
                    user_id=request.user.id,
                    status="CREATED",
                    risk_level=f"Score_{risk_score}"
                )
                
                # Check if OTP is required (high risk transactions)
                if risk_score >= 70 or requires_otp:
                    # Set transaction to pending and require OTP
                    transaction_obj.status = 'pending'
                    transaction_obj.save()
                    
                    # Create and send OTP
                    otp_obj = create_transaction_otp(transaction_obj, request.user)
                    
                    if otp_obj:
                        logger.info(f"High risk transaction requires OTP: ID {transaction_obj.id}, Risk score: {risk_score}")
                        
                        # Create fraud alert
                        fraud_alert = risk_engine.create_fraud_alert(transaction_obj, risk_score, triggers)
                        
                        # Log high risk transaction
                        log_system_event(
                            "High risk transaction requires OTP verification",
                            "transactions",
                            "WARNING",
                            {
                                "transaction_id": transaction_obj.id,
                                "risk_score": risk_score,
                                "triggers": triggers,
                                "user_id": request.user.id
                            }
                        )
                        
                        return Response({
                            'message': 'Transaction created but requires OTP verification due to high risk.',
                            'transaction_id': transaction_obj.id,
                            'risk_score': risk_score,
                            'status': 'pending',
                            'requires_otp': True,
                            'otp_sent': True
                        }, status=status.HTTP_201_CREATED)
                    else:
                        # OTP creation failed
                        logger.error(f"Failed to create OTP for high risk transaction {transaction_obj.id}")
                        transaction_obj.status = 'failed'
                        transaction_obj.save()
                        
                        return Response({
                            'error': 'Failed to send verification code. Please try again.'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                elif risk_score >= 40:  # Medium risk - complete with alert
                    # Update balances for completed transaction
                    self._update_balances(transaction_obj, client_profile)
                    
                    transaction_obj.status = 'completed'
                    transaction_obj.save()
                    
                    # Create fraud alert but don't block
                    fraud_alert = risk_engine.create_fraud_alert(transaction_obj, risk_score, triggers)
                    logger.info(f"Medium risk transaction completed: ID {transaction_obj.id}, Risk score: {risk_score}")
                    
                    # Send transaction notification email
                    if transaction_obj.client.user:
                        risk_level = "MEDIUM" if risk_score >= 50 else "LOW"
                        send_transaction_notification(
                            transaction_obj.client.user, 
                            transaction_obj, 
                            "COMPLETED", 
                            risk_level
                        )
                    
                    return Response({
                        'message': 'Transaction completed with medium risk alert.',
                        'transaction_id': transaction_obj.id,
                        'risk_score': risk_score,
                        'status': 'completed'
                    }, status=status.HTTP_201_CREATED)
                
                else:  # Low risk - complete normally
                    # Update balances for completed transaction
                    self._update_balances(transaction_obj, client_profile)
                    
                    transaction_obj.status = 'completed'
                    transaction_obj.save()
                    
                    logger.info(f"Low risk transaction completed: ID {transaction_obj.id}, Risk score: {risk_score}")
                    
                    # Send transaction notification email
                    if transaction_obj.client.user:
                        send_transaction_notification(
                            transaction_obj.client.user, 
                            transaction_obj, 
                            "COMPLETED", 
                            "LOW"
                        )
                    
                    return Response({
                        'message': 'Transaction completed successfully.',
                        'transaction_id': transaction_obj.id,
                        'risk_score': risk_score,
                        'status': 'completed'
                    }, status=status.HTTP_201_CREATED)
                    
            except ClientProfile.DoesNotExist:
                logger.error(f"Client profile not found for user {request.user.email}")
                return Response({
                    'error': 'Client profile not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating transaction: {e}")
                return Response({
                    'error': 'Transaction creation failed'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.error(f"Transaction validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def verify_otp(self, request, pk=None):
        """Verify OTP for a pending transaction"""
        try:
            transaction_obj = self.get_object()
            
            if transaction_obj.status != 'pending':
                return Response({
                    'error': 'Transaction is not pending OTP verification'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            otp_code = request.data.get('otp')
            if not otp_code:
                return Response({
                    'error': 'OTP code is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify OTP
            result = verify_transaction_otp(transaction_obj.id, otp_code, request.user)
            
            if result['success']:
                # OTP verified - complete the transaction
                try:
                    with transaction.atomic():
                        # Update balances
                        self._update_balances(transaction_obj, transaction_obj.client)
                        
                        # Mark transaction as completed
                        transaction_obj.status = 'completed'
                        transaction_obj.save()
                        
                        logger.info(f"Transaction {transaction_obj.id} completed after OTP verification")
                        
                        # Send transaction notification email
                        if transaction_obj.client.user:
                            risk_level = "HIGH" if transaction_obj.risk_score >= 70 else "MEDIUM"
                            send_transaction_notification(
                                transaction_obj.client.user, 
                                transaction_obj, 
                                "COMPLETED", 
                                risk_level
                            )
                        
                        return Response({
                            'message': 'Transaction completed successfully after OTP verification.',
                            'transaction_id': transaction_obj.id,
                            'status': 'completed'
                        })
                        
                except Exception as e:
                    logger.error(f"Error completing transaction after OTP verification: {e}")
                    return Response({
                        'error': 'Failed to complete transaction'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in OTP verification: {e}")
            return Response({
                'error': 'OTP verification failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def resend_otp(self, request, pk=None):
        """Resend OTP for a pending transaction"""
        try:
            transaction_obj = self.get_object()
            
            if transaction_obj.status != 'pending':
                return Response({
                    'error': 'Transaction is not pending OTP verification'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Resend OTP
            success = resend_transaction_otp(transaction_obj.id, request.user)
            
            if success:
                return Response({
                    'message': 'OTP resent successfully'
                })
            else:
                return Response({
                    'error': 'Failed to resend OTP'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error resending OTP: {e}")
            return Response({
                'error': 'Failed to resend OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_balances(self, transaction_obj, client_profile):
        """Update balances for completed transactions"""
        try:
            amount = transaction_obj.amount
            
            logger.info(f"Updating balances for transaction {transaction_obj.id}")
            logger.info(f"Current balance: {client_profile.balance}, Amount: {amount}")
            
            # Only transfer logic remains
            # Deduct from sender
            client_profile.balance -= amount
            logger.info(f"Transfer (sender): New balance = {client_profile.balance}")
            
            # Add to recipient if account exists
            recipient_account = transaction_obj.to_account_number
            try:
                recipient_profile = ClientProfile.objects.get(bank_account_number=recipient_account)
                recipient_profile.balance += amount
                recipient_profile.save()
                logger.info(f"Transfer (recipient): Account {recipient_account}, New balance = {recipient_profile.balance}")
            except ClientProfile.DoesNotExist:
                logger.warning(f"Recipient account {recipient_account} not found for transfer")
            
            client_profile.save()
            logger.info(f"Balance update completed for client {client_profile.full_name}. "
                       f"New balance: {client_profile.balance} DZD")
            
        except Exception as e:
            logger.error(f"Error updating balances: {e}")
            raise

class FraudAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """Fraud alert viewset for clients"""
    serializer_class = FraudAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            client_profile = ClientProfile.objects.get(user=self.request.user)
            return FraudAlert.objects.filter(transaction__client=client_profile)
        except ClientProfile.DoesNotExist:
            return FraudAlert.objects.none()

class AdminTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin transaction viewset"""
    serializer_class = AdminTransactionSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Transaction.objects.all()
    
    def get_queryset(self):
        queryset = Transaction.objects.all()
        
        # Filter by client
        client_id = self.request.query_params.get('client_id', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('transaction_type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset

class AdminFraudAlertViewSet(viewsets.ModelViewSet):
    """Admin fraud alert viewset"""
    serializer_class = AdminFraudAlertSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FraudAlert.objects.all()
    
    def get_queryset(self):
        queryset = FraudAlert.objects.all()
        
        # Filter by level
        level = self.request.query_params.get('level', None)
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve a fraud alert and complete the transaction"""
        logger.info(f"Admin {request.user.email} approving fraud alert {pk}")
        
        fraud_alert = self.get_object()
        
        if fraud_alert.status == 'Reviewed':
            logger.warning(f"Fraud alert {pk} already reviewed")
            return Response({'message': 'Alert already reviewed'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Update fraud alert status
                fraud_alert.status = 'Reviewed'
                fraud_alert.save()
                
                # Complete the transaction and update balances
                transaction_obj = fraud_alert.transaction
                transaction_obj.status = 'completed'
                transaction_obj.save()
                
                # Update balances for the completed transaction
                self._update_balances(transaction_obj, transaction_obj.client)
                
                # Send transaction notification email
                if transaction_obj.client.user:
                    send_transaction_notification(
                        transaction_obj.client.user, 
                        transaction_obj, 
                        "APPROVED", 
                        "REVIEWED"
                    )
                
                logger.info(f"Fraud alert {pk} approved, transaction {transaction_obj.id} completed")
                
                return Response({'message': 'Transaction approved and completed'})
                
        except Exception as e:
            logger.error(f"Error approving fraud alert {pk}: {e}")
            return Response({'error': 'Failed to approve transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Reject a fraud alert and fail the transaction"""
        logger.info(f"Admin {request.user.email} rejecting fraud alert {pk}")
        
        fraud_alert = self.get_object()
        
        if fraud_alert.status == 'Reviewed':
            logger.warning(f"Fraud alert {pk} already reviewed")
            return Response({'message': 'Alert already reviewed'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Update fraud alert status
            fraud_alert.status = 'Reviewed'
            fraud_alert.save()
            
            # Fail the transaction
            transaction_obj = fraud_alert.transaction
            transaction_obj.status = 'failed'
            transaction_obj.save()
            
            # Send transaction notification email
            if transaction_obj.client.user:
                send_transaction_notification(
                    transaction_obj.client.user, 
                    transaction_obj, 
                    "REJECTED", 
                    "BLOCKED"
                )
            
            logger.info(f"Fraud alert {pk} rejected, transaction {transaction_obj.id} failed")
            
            return Response({'message': 'Transaction rejected and failed'})
            
        except Exception as e:
            logger.error(f"Error rejecting fraud alert {pk}: {e}")
            return Response({'error': 'Failed to reject transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_balances(self, transaction_obj, client_profile):
        """Update balances for completed transactions (same as in TransactionViewSet)"""
        try:
            amount = transaction_obj.amount
            transaction_type = transaction_obj.transaction_type
            
            logger.info(f"Admin updating balances for transaction {transaction_obj.id}")
            
            if transaction_type == 'deposit':
                client_profile.balance += amount
            elif transaction_type == 'withdraw':
                client_profile.balance -= amount
            elif transaction_type == 'transfer':
                # Deduct from sender
                client_profile.balance -= amount
                
                # Add to recipient if account exists
                recipient_account = transaction_obj.to_account_number
                try:
                    recipient_profile = ClientProfile.objects.get(bank_account_number=recipient_account)
                    recipient_profile.balance += amount
                    recipient_profile.save()
                    logger.info(f"Transfer (recipient): Account {recipient_account}, New balance = {recipient_profile.balance}")
                except ClientProfile.DoesNotExist:
                    logger.warning(f"Recipient account {recipient_account} not found for transfer")
            
            client_profile.save()
            logger.info(f"Admin balance update completed for client {client_profile.full_name}")
            
        except Exception as e:
            logger.error(f"Error updating balances in admin view: {e}")
            raise
