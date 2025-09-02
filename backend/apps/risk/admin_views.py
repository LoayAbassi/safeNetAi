from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Threshold, Rule, ClientProfile
from .serializers import ThresholdSerializer, RuleSerializer
from apps.users.serializers import AdminClientProfileSerializer
from apps.transactions.serializers import AdminTransactionSerializer, AdminFraudAlertSerializer
from apps.transactions.models import Transaction, FraudAlert
from django.db import models
from apps.utils.logger import get_system_logger

# Set up logger
logger = get_system_logger()

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", "") == "ADMIN"

class RuleViewSet(viewsets.ModelViewSet):
    """Admin viewset for managing fraud detection rules"""
    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Rule.objects.all()

class ThresholdViewSet(viewsets.ModelViewSet):
    """Admin viewset for managing fraud detection thresholds"""
    serializer_class = ThresholdSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Threshold.objects.all()

class ClientProfileAdminViewSet(viewsets.ModelViewSet):
    """Admin viewset for managing client profiles"""
    serializer_class = AdminClientProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ClientProfile.objects.all()
    
    def get_queryset(self):
        queryset = ClientProfile.objects.all()
        
        # Search by name or national_id
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(national_id__icontains=search) |
                models.Q(bank_account_number__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Create profile with auto-generated bank account number"""
        serializer.save()

class TransactionAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin viewset for viewing all transactions"""
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

class FraudAlertAdminViewSet(viewsets.ModelViewSet):
    """Admin viewset for managing fraud alerts"""
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
        fraud_alert = self.get_object()
        
        if fraud_alert.status == 'Reviewed':
            return Response({'message': 'Alert already reviewed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update fraud alert status
        fraud_alert.status = 'Reviewed'
        fraud_alert.save()
        
        # Complete the transaction
        transaction = fraud_alert.transaction
        transaction.status = 'completed'
        transaction.save()
        
        return Response({'message': 'Transaction approved and completed'})
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Reject a fraud alert and fail the transaction"""
        fraud_alert = self.get_object()
        
        if fraud_alert.status == 'Reviewed':
            return Response({'message': 'Alert already reviewed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update fraud alert status
        fraud_alert.status = 'Reviewed'
        fraud_alert.save()
        
        # Fail the transaction
        transaction = fraud_alert.transaction
        transaction.status = 'failed'
        transaction.save()
        
        return Response({'message': 'Transaction rejected and failed'})

class DashboardViewSet(viewsets.ViewSet):
    """Dashboard statistics for admin users"""
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        try:
            # Calculate date ranges
            now = timezone.now()
            last_month = now - timedelta(days=30)
            last_week = now - timedelta(days=7)
            
            # Basic counts
            total_clients = ClientProfile.objects.count()
            total_transactions = Transaction.objects.count()
            pending_alerts = FraudAlert.objects.filter(status='Active').count()
            total_balance = ClientProfile.objects.aggregate(total=Sum('balance'))['total'] or 0
            
            # Recent activity (last 7 days)
            recent_transactions = Transaction.objects.filter(
                created_at__gte=last_week
            ).count()
            
            recent_alerts = FraudAlert.objects.filter(
                created_at__gte=last_week
            ).count()
            
            # Monthly changes
            last_month_clients = ClientProfile.objects.filter(
                created_at__gte=last_month
            ).count()
            
            last_month_transactions = Transaction.objects.filter(
                created_at__gte=last_month
            ).count()
            
            # Calculate percentage changes
            client_change = ((total_clients - last_month_clients) / max(last_month_clients, 1)) * 100 if last_month_clients > 0 else 0
            transaction_change = ((total_transactions - last_month_transactions) / max(last_month_transactions, 1)) * 100 if last_month_transactions > 0 else 0
            
            # Risk distribution
            risk_distribution = {
                'low': FraudAlert.objects.filter(level='LOW').count(),
                'medium': FraudAlert.objects.filter(level='MEDIUM').count(),
                'high': FraudAlert.objects.filter(level='HIGH').count(),
                'critical': FraudAlert.objects.filter(level='CRITICAL').count()
            }
            
            stats = {
                'total_clients': total_clients,
                'total_transactions': total_transactions,
                'pending_alerts': pending_alerts,
                'total_balance': float(total_balance),
                'recent_transactions': recent_transactions,
                'recent_alerts': recent_alerts,
                'changes': {
                    'clients': round(client_change, 1),
                    'transactions': round(transaction_change, 1)
                },
                'risk_distribution': risk_distribution
            }
            
            logger.info(f"Dashboard stats requested by admin {request.user.email}")
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error fetching dashboard stats: {e}")
            return Response(
                {'error': 'Failed to fetch dashboard statistics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent transactions and alerts"""
        try:
            # Recent transactions (last 10)
            recent_transactions = Transaction.objects.select_related('client').order_by('-created_at')[:10]
            
            # Recent fraud alerts (last 10)
            recent_alerts = FraudAlert.objects.select_related('transaction__client').order_by('-created_at')[:10]
            
            # Serialize data
            from apps.transactions.serializers import AdminTransactionSerializer
            from apps.transactions.serializers import AdminFraudAlertSerializer
            
            transaction_data = AdminTransactionSerializer(recent_transactions, many=True).data
            alert_data = AdminFraudAlertSerializer(recent_alerts, many=True).data
            
            recent_activity = {
                'transactions': transaction_data,
                'alerts': alert_data
            }
            
            logger.info(f"Recent activity requested by admin {request.user.email}")
            return Response(recent_activity)
            
        except Exception as e:
            logger.error(f"Error fetching recent activity: {e}")
            return Response(
                {'error': 'Failed to fetch recent activity'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
