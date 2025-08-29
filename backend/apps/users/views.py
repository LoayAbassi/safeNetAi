from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, ClientProfile
from .serializers import (
    UserSerializer, 
    ClientProfileSerializer
)
from apps.risk.serializers import ClientProfileAdminSerializer

class IsClient(permissions.BasePermission):
    """Permission to check if user is a client"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'clientprofile')

class IsAdmin(permissions.BasePermission):
    """Permission to check if user is an admin"""
    def has_permission(self, request, view):
        return getattr(request.user, 'role', '') == 'ADMIN'

class ClientProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for client profiles - clients can only see their own profile
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]
    
    def get_queryset(self):
        """Clients can only see their own profile"""
        return ClientProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        try:
            profile = request.user.clientprofile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except ClientProfile.DoesNotExist:
            return Response(
                {'error': 'No profile found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AdminClientProfileViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for managing all client profiles
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
