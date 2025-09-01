from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Threshold, Rule, ClientProfile
from .serializers import ThresholdSerializer, RuleSerializer
from apps.users.serializers import AdminClientProfileSerializer
from apps.transactions.serializers import AdminTransactionSerializer, AdminFraudAlertSerializer
from apps.transactions.models import Transaction, FraudAlert
from django.db import models

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
