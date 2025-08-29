from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Threshold, Rule
from .serializers import (
    ThresholdSerializer, 
    RuleSerializer,
    ClientProfileAdminSerializer,
    TransactionAdminSerializer,
    FraudAlertAdminSerializer
)
from apps.users.models import ClientProfile
from apps.transactions.models import Transaction, FraudAlert

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", "") == "ADMIN"

class ThresholdViewSet(viewsets.ModelViewSet):
    queryset = Threshold.objects.all()
    serializer_class = ThresholdSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class ClientProfileAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing client profiles
    """
    queryset = ClientProfile.objects.all().order_by('-created_at')
    serializer_class = ClientProfileAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search clients by name or national ID"""
        query = request.query_params.get('q', '')
        if query:
            queryset = self.queryset.filter(
                full_name__icontains=query
            ) | self.queryset.filter(
                national_id__icontains=query
            )
        else:
            queryset = self.queryset
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TransactionAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin ViewSet for viewing all transactions
    """
    queryset = Transaction.objects.all().order_by('-timestamp')
    serializer_class = TransactionAdminSerializer
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

class FraudAlertAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing fraud alerts
    """
    queryset = FraudAlert.objects.all().order_by('-created_at')
    serializer_class = FraudAlertAdminSerializer
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
