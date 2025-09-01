from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import ClientProfileSerializer, AdminClientProfileSerializer
from apps.risk.models import ClientProfile
from django.db import models

class ClientProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Client profile viewset for authenticated users"""
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ClientProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        try:
            profile = ClientProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except ClientProfile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AdminClientProfileViewSet(viewsets.ModelViewSet):
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

class VerifyOTPView(viewsets.ViewSet):
    """OTP verification viewset"""
    permission_classes = [permissions.AllowAny]
    
    def create(self, request):
        from .serializers import OTPVerificationSerializer
        from rest_framework_simplejwt.tokens import RefreshToken
        
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            otp_obj = serializer.validated_data['otp_obj']
            
            # Mark OTP as used
            otp_obj.mark_used()
            
            # Mark user as verified
            user.is_email_verified = True
            user.save()
            
            # Link user to client profile
            try:
                profile = ClientProfile.objects.get(
                    first_name__iexact=user.first_name,
                    last_name__iexact=user.last_name
                )
                profile.user = user
                profile.save()
            except ClientProfile.DoesNotExist:
                pass
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Email verified successfully.',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
