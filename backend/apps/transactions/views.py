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
from apps.risk.engine import RiskEngine, haversine_distance
from apps.risk.ml import FraudMLModel
from apps.users.email_service import send_fraud_alert_email, send_transaction_notification
from apps.transactions.services import create_transaction_otp, verify_transaction_otp, resend_transaction_otp
from apps.utils.logger import get_transactions_logger, log_transaction, log_system_event
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import random
import string

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
                
                # ENHANCED LOCATION VALIDATION AND INTEGRITY CHECKS
                # Extract location data from request
                current_location = request.data.get('current_location', {})
                transaction_lat = current_location.get('lat', 0.0) if current_location else 0.0
                transaction_lng = current_location.get('lng', 0.0) if current_location else 0.0
                
                # Primary validation: Block transactions with zero coordinates (often fake/VPN)
                if transaction_lat == 0.0 and transaction_lng == 0.0:
                    logger.warning(f"Transaction blocked: Invalid location coordinates (0.0, 0.0) for user {request.user.email}")
                    log_transaction(
                        transaction_id=0,  # Not created yet
                        amount=serializer.validated_data.get('amount'),
                        transaction_type=serializer.validated_data.get('transaction_type'),
                        user_id=request.user.id,
                        status="REJECTED_INVALID_LOCATION"
                    )
                    return Response({
                        'error': 'Transaction blocked: Location verification required. Please ensure your location services are enabled and try again.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Coordinate range validation (basic sanity check)
                if not (-90 <= transaction_lat <= 90) or not (-180 <= transaction_lng <= 180):
                    logger.warning(f"Transaction blocked: Invalid location coordinates ({transaction_lat}, {transaction_lng}) for user {request.user.email}")
                    log_transaction(
                        transaction_id=0,
                        amount=serializer.validated_data.get('amount'),
                        transaction_type=serializer.validated_data.get('transaction_type'),
                        user_id=request.user.id,
                        status="REJECTED_INVALID_COORDINATES"
                    )
                    return Response({
                        'error': 'Transaction blocked: Invalid location coordinates detected.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Additional integrity checks
                suspicious_patterns = []
                
                # Check for exact coordinate repeats (possible fake location)
                if (abs(transaction_lat - round(transaction_lat)) == 0.0 and 
                    abs(transaction_lng - round(transaction_lng)) == 0.0):
                    suspicious_patterns.append("Exact integer coordinates (possible fake)")
                
                # Check for common fake coordinates
                fake_coordinates = [
                    (0.0, 0.0),     # Null Island
                    (37.4419, -122.1430),  # Google HQ (common VPN endpoint)
                    (40.7589, -73.9851),   # Times Square (common fake location)
                    (51.5074, -0.1278),    # London center
                    (48.8566, 2.3522),     # Paris center
                ]
                
                for fake_lat, fake_lng in fake_coordinates:
                    if (abs(transaction_lat - fake_lat) < 0.001 and 
                        abs(transaction_lng - fake_lng) < 0.001):
                        suspicious_patterns.append(f"Matches known fake location: ({fake_lat}, {fake_lng})")
                
                # Check for extremely rapid location changes (teleportation detection)
                if (client_profile.last_known_lat and client_profile.last_known_lng):
                    prev_distance = haversine_distance(
                        float(client_profile.last_known_lat), float(client_profile.last_known_lng),
                        transaction_lat, transaction_lng
                    )
                    
                    # Check recent transactions for time calculation
                    recent_transaction = Transaction.objects.filter(
                        client=client_profile
                    ).order_by('-created_at').first()
                    
                    if recent_transaction:
                        time_diff = timezone.now() - recent_transaction.created_at
                        time_hours = time_diff.total_seconds() / 3600
                        
                        # If moved more than 500km in less than 1 hour (impossible without flight)
                        if prev_distance > 500 and time_hours < 1:
                            suspicious_patterns.append(f"Impossible travel: {prev_distance:.1f}km in {time_hours:.1f}h")
                
                # Log suspicious patterns but don't block (just add to risk assessment)
                if suspicious_patterns:
                    logger.warning(f"Suspicious location patterns detected for user {request.user.email}: {suspicious_patterns}")
                
                logger.info(f"Location validation passed: ({transaction_lat}, {transaction_lng})")
                
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
                
                # UPDATE CLIENT PROFILE LOCATION FIELDS
                # Set home location if not set (first transaction)
                if not client_profile.home_lat or not client_profile.home_lng:
                    client_profile.home_lat = Decimal(str(transaction_lat))
                    client_profile.home_lng = Decimal(str(transaction_lng))
                    logger.info(f"Setting home location for user {request.user.email}: ({transaction_lat}, {transaction_lng})")
                
                # ALWAYS update last known location on EVERY transaction attempt
                # This is critical for distance-based fraud detection
                client_profile.last_known_lat = Decimal(str(transaction_lat))
                client_profile.last_known_lng = Decimal(str(transaction_lng))
                client_profile.save()
                logger.info(f"Updated last known location for user {request.user.email}: ({transaction_lat}, {transaction_lng})")
                
                # Log comprehensive location details
                logger.info(f"Location tracking: User={request.user.email}, "
                          f"Home=({client_profile.home_lat}, {client_profile.home_lng}), "
                          f"Current=({transaction_lat}, {transaction_lng}), "
                          f"Last Known=({client_profile.last_known_lat}, {client_profile.last_known_lng})")
                
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
                
                # Check if OTP is required (Enhanced logic for distance-based fraud detection)
                # OTP required if:
                # 1. Any business rules triggered (len(triggers) > 0)
                # 2. High risk score (>= 70)
                # 3. High AI score (ml_score >= 0.6)
                # 4. Explicit requires_otp flag (including distance violations)
                # 5. MANDATORY: Distance-based violations (cannot be bypassed)
                
                # Check for distance-based violations (these ALWAYS require OTP)
                distance_violation = any('distance exceeded' in trigger.lower() for trigger in triggers)
                
                requires_otp_final = (
                    len(triggers) > 0 or           # ANY rule triggered
                    risk_score >= 70 or            # High combined risk score
                    ml_score >= 0.6 or             # High AI risk score
                    requires_otp or                # Explicit OTP requirement from risk engine
                    distance_violation             # MANDATORY: Distance-based fraud detection
                )
                
                # Log OTP decision reasoning
                otp_reasons = []
                if len(triggers) > 0:
                    otp_reasons.append(f"Business rules triggered: {len(triggers)}")
                if risk_score >= 70:
                    otp_reasons.append(f"High risk score: {risk_score}")
                if ml_score >= 0.6:
                    otp_reasons.append(f"High AI score: {ml_score:.3f}")
                if requires_otp:
                    otp_reasons.append("Risk engine explicit requirement")
                if distance_violation:
                    otp_reasons.append("MANDATORY distance violation")
                
                logger.info(f"OTP decision for transaction {transaction_obj.id}: "
                           f"Required={requires_otp_final}, Reasons={otp_reasons}")
                
                if requires_otp_final:
                    # Set transaction to pending and require OTP
                    transaction_obj.status = 'pending'
                    transaction_obj.save()
                    
                    # Create and send OTP
                    otp_obj = create_transaction_otp(transaction_obj, request.user)
                    
                    if otp_obj:
                        logger.info(f"Transaction requires OTP verification: ID {transaction_obj.id}, "
                                  f"Risk score: {risk_score}, Triggers: {len(triggers)}, ML score: {ml_score:.3f}")
                        
                        # Create fraud alert
                        fraud_alert = risk_engine.create_fraud_alert(transaction_obj, risk_score, triggers)
                        
                        # Log high risk transaction with enhanced details
                        log_system_event(
                            "Transaction requires OTP verification due to risk rules or AI assessment",
                            "transactions",
                            "WARNING",
                            {
                                "transaction_id": transaction_obj.id,
                                "risk_score": risk_score,
                                "triggers": triggers,
                                "ml_score": ml_score,
                                "user_id": request.user.id,
                                "distance_violation": distance_violation,
                                "otp_reasons": otp_reasons,
                                "reason": "distance_violation" if distance_violation else "risk_rules" if len(triggers) > 0 else "ai_assessment" if ml_score >= 0.6 else "high_score"
                            }
                        )
                        
                        return Response({
                            'message': 'Transaction created but requires OTP verification due to risk assessment.',
                            'transaction_id': transaction_obj.id,
                            'risk_score': risk_score,
                            'ml_score': ml_score,
                            'triggers': triggers,
                            'status': 'pending',
                            'requires_otp': True,
                            'otp_sent': True,
                            'distance_violation': distance_violation,
                            'otp_reasons': otp_reasons
                        }, status=status.HTTP_201_CREATED)
                    else:
                        # OTP creation failed
                        logger.error(f"Failed to create OTP for risk-flagged transaction {transaction_obj.id}")
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
                
                # Update recipient's statistics as well
                self._update_client_statistics(recipient_profile)
                
            except ClientProfile.DoesNotExist:
                logger.warning(f"Recipient account {recipient_account} not found for transfer")
            
            client_profile.save()
            
            # Update client statistics after balance change
            self._update_client_statistics(client_profile)
            
            logger.info(f"Balance update completed for client {client_profile.full_name}. "
                       f"New balance: {client_profile.balance} DZD")
            
        except Exception as e:
            logger.error(f"Error updating balances: {e}")
            raise
    
    def _update_client_statistics(self, client_profile):
        """Update client profile statistics (avg_amount, std_amount) based on transaction history"""
        try:
            from django.db.models import Avg, StdDev, Count
            from decimal import Decimal
            import math
            
            logger.info(f"Updating statistics for client {client_profile.full_name}")
            
            # Get all completed transactions for this client
            completed_transactions = Transaction.objects.filter(
                client=client_profile,
                status='completed'
            )
            
            if completed_transactions.exists():
                # Calculate statistics
                stats = completed_transactions.aggregate(
                    avg_amount=Avg('amount'),
                    std_amount=StdDev('amount'),
                    transaction_count=Count('id')
                )
                
                # Update client profile with calculated statistics
                client_profile.avg_amount = Decimal(str(stats['avg_amount'] or 0))
                
                # Handle standard deviation (can be None if only one transaction)
                std_dev = stats['std_amount'] or 0
                client_profile.std_amount = Decimal(str(std_dev))
                
                client_profile.save()
                
                logger.info(f"Statistics updated for {client_profile.full_name}: "
                          f"avg_amount={client_profile.avg_amount}, "
                          f"std_amount={client_profile.std_amount}, "
                          f"transaction_count={stats['transaction_count']}")
            else:
                logger.info(f"No completed transactions found for client {client_profile.full_name}")
                
        except Exception as e:
            logger.error(f"Error updating client statistics for {client_profile.full_name}: {e}")

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
                    
                    # Update recipient's statistics
                    self._update_client_statistics(recipient_profile)
                    
                except ClientProfile.DoesNotExist:
                    logger.warning(f"Recipient account {recipient_account} not found for transfer")
            
            client_profile.save()
            
            # Update client statistics after balance change
            self._update_client_statistics(client_profile)
            
            logger.info(f"Admin balance update completed for client {client_profile.full_name}")
            
        except Exception as e:
            logger.error(f"Error updating balances in admin view: {e}")
            raise
    
    def _update_client_statistics(self, client_profile):
        """Update client profile statistics - same as in TransactionViewSet"""
        try:
            from django.db.models import Avg, StdDev, Count
            from decimal import Decimal
            
            logger.info(f"Admin updating statistics for client {client_profile.full_name}")
            
            # Get all completed transactions for this client
            completed_transactions = Transaction.objects.filter(
                client=client_profile,
                status='completed'
            )
            
            if completed_transactions.exists():
                # Calculate statistics
                stats = completed_transactions.aggregate(
                    avg_amount=Avg('amount'),
                    std_amount=StdDev('amount'),
                    transaction_count=Count('id')
                )
                
                # Update client profile with calculated statistics
                client_profile.avg_amount = Decimal(str(stats['avg_amount'] or 0))
                
                # Handle standard deviation (can be None if only one transaction)
                std_dev = stats['std_amount'] or 0
                client_profile.std_amount = Decimal(str(std_dev))
                
                client_profile.save()
                
                logger.info(f"Admin statistics updated for {client_profile.full_name}: "
                          f"avg_amount={client_profile.avg_amount}, "
                          f"std_amount={client_profile.std_amount}, "
                          f"transaction_count={stats['transaction_count']}")
            else:
                logger.info(f"No completed transactions found for client {client_profile.full_name}")
                
        except Exception as e:
            logger.error(f"Error updating client statistics for {client_profile.full_name}: {e}")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_security_otp(request):
    """Send security OTP for high-risk transactions"""
    try:
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response({'error': 'Transaction ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get transaction
        try:
            transaction = Transaction.objects.get(id=transaction_id, client__user=request.user)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if transaction is pending OTP
        if transaction.status != 'pending':
            return Response({'error': 'Transaction does not require OTP verification'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Create or update OTP
        otp_obj, created = TransactionOTP.objects.update_or_create(
            transaction=transaction,
            user=request.user,
            defaults={
                'otp': otp,
                'expires_at': expires_at,
                'attempts': 0,
                'used': False
            }
        )
        
        # Send OTP via email (in production, this would be SMS or push notification)
        try:
            from apps.users.email_service import send_security_otp_email
            send_security_otp_email(request.user, otp, transaction)
        except Exception as e:
            logger.warning(f"Failed to send security OTP email: {e}")
        
        logger.info(f"Security OTP sent for transaction {transaction_id}")
        
        return Response({
            'message': 'Security OTP sent successfully',
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error sending security OTP: {e}")
        return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_security_otp(request):
    """Verify security OTP and complete transaction"""
    try:
        transaction_id = request.data.get('transaction_id')
        otp_code = request.data.get('otp')
        
        if not transaction_id or not otp_code:
            return Response({'error': 'Transaction ID and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get transaction
        try:
            transaction = Transaction.objects.get(id=transaction_id, client__user=request.user)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if transaction is pending OTP
        if transaction.status != 'pending':
            return Response({'error': 'Transaction does not require OTP verification'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        try:
            otp_obj = TransactionOTP.objects.get(
                transaction=transaction,
                user=request.user,
                otp=otp_code,
                used=False
            )
        except TransactionOTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check attempts
        if otp_obj.attempts >= 3:
            return Response({'error': 'Too many OTP attempts'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark OTP as used
        otp_obj.mark_used()
        
        # Complete the transaction
        try:
            with transaction.atomic():
                # Update balances using the TransactionViewSet method
                viewset = TransactionViewSet()
                viewset._update_balances(transaction, transaction.client)
                
                # Mark transaction as completed
                transaction.status = 'completed'
                transaction.save()
                
                logger.info(f"Transaction {transaction.id} completed after security OTP verification")
                
                # Send transaction notification email
                if transaction.client.user:
                    risk_level = "HIGH" if transaction.risk_score >= 70 else "MEDIUM"
                    send_transaction_notification(
                        transaction.client.user, 
                        transaction, 
                        "COMPLETED", 
                        risk_level
                    )
                
                return Response({
                    'message': 'Transaction completed successfully after security verification.',
                    'transaction_id': transaction.id,
                    'status': 'completed'
                })
                
        except Exception as e:
            logger.error(f"Error completing transaction after OTP verification: {e}")
            return Response({'error': 'Failed to complete transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error verifying security OTP: {e}")
        return Response({'error': 'Failed to verify OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
