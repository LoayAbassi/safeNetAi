from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Transaction, FraudAlert
from .serializers import (
    TransactionSerializer, 
    TransactionCreateSerializer,
    FraudAlertSerializer
)
from apps.users.serializers import ClientProfileSerializer

class IsClient(permissions.BasePermission):
    """Permission to check if user is a client"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'clientprofile')

class IsAdmin(permissions.BasePermission):
    """Permission to check if user is an admin"""
    def has_permission(self, request, view):
        return getattr(request.user, 'role', '') == 'ADMIN'

class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for transactions - clients can only see their own transactions
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]
    
    def get_queryset(self):
        """Clients can only see their own transactions"""
        return Transaction.objects.filter(client__user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer

class FraudAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for fraud alerts - read-only for clients
    """
    serializer_class = FraudAlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]
    
    def get_queryset(self):
        """Clients can only see alerts for their own transactions"""
        return FraudAlert.objects.filter(transaction__client__user=self.request.user)

# Admin Views
class AdminTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin ViewSet for viewing all transactions
    """
    queryset = Transaction.objects.all().order_by('-timestamp')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search transactions by client name or national ID"""
        query = request.query_params.get('q', '')
        if query:
            queryset = self.queryset.filter(
                client__full_name__icontains=query
            ) | self.queryset.filter(
                client__national_id__icontains=query
            )
        else:
            queryset = self.queryset
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AdminFraudAlertViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing fraud alerts
    """
    queryset = FraudAlert.objects.all().order_by('-created_at')
    serializer_class = FraudAlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update fraud alert status"""
        alert = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in ['Pending', 'Reviewed']:
            alert.status = new_status
            alert.save()
            serializer = self.get_serializer(alert)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
