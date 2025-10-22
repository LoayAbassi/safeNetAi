from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.cache import cache
from .serializers import (
    LoginSerializer, UserRegistrationSerializer, OTPVerificationSerializer, ResendOTPSerializer
)
from .email_service import create_otp_for_user
from apps.risk.models import ClientProfile
from apps.utils.logger import log_user_action, log_security_event

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Update user's language preference if provided
        language = request.data.get('language')
        if language and language in ['en', 'fr', 'ar']:
            user.language = language
            user.save()
        
        # Log successful login
        log_user_action(
            action="LOGIN",
            user_id=user.id,
            user_email=user.email,
            success=True,
            extra_data={"ip_address": request.META.get('REMOTE_ADDR')}
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'role': 'admin' if user.is_superuser else 'client',
                'language': user.language
            }
        })
    else:
        # Log failed login attempt
        email = request.data.get('email', 'unknown')
        log_security_event(
            event="Failed login attempt",
            ip_address=request.META.get('REMOTE_ADDR'),
            extra_data={"email": email, "errors": serializer.errors}
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Update user's language preference if provided
        language = request.data.get('language')
        if language and language in ['en', 'fr', 'ar']:
            user.language = language
            user.save()
        
        # Log successful registration
        log_user_action(
            action="REGISTRATION",
            user_id=user.id,
            user_email=user.email,
            success=True,
            extra_data={"ip_address": request.META.get('REMOTE_ADDR')}
        )
        
        # Create and send OTP
        otp = create_otp_for_user(user)
        
        if otp:
            return Response({
                'message': 'Registration successful. Please check your email for OTP verification.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Registration successful but failed to send OTP. Please contact support.'
            }, status=status.HTTP_201_CREATED)
    else:
        # Log failed registration attempt
        email = request.data.get('email', 'unknown')
        log_security_event(
            event="Failed registration attempt",
            ip_address=request.META.get('REMOTE_ADDR'),
            extra_data={"email": email, "errors": serializer.errors}
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    """OTP verification endpoint"""
    serializer = OTPVerificationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']
        
        # Mark OTP as used
        otp_obj.mark_used()
        
        # Mark user as verified
        user.is_email_verified = True
        user.save()
        
        # Log successful OTP verification
        log_user_action(
            action="OTP_VERIFICATION",
            user_id=user.id,
            user_email=user.email,
            success=True,
            extra_data={"ip_address": request.META.get('REMOTE_ADDR')}
        )
        
        # Link user to client profile
        try:
            profile = ClientProfile.objects.get(
                first_name__iexact=user.first_name,
                last_name__iexact=user.last_name
            )
            profile.user = user
            profile.save()
        except ClientProfile.DoesNotExist:
            pass  # Profile might not exist yet
        
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
    else:
        # Log failed OTP verification
        email = request.data.get('email', 'unknown')
        log_security_event(
            event="Failed OTP verification",
            ip_address=request.META.get('REMOTE_ADDR'),
            extra_data={"email": email, "errors": serializer.errors}
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp_view(request):
    """Resend OTP endpoint with rate limiting"""
    serializer = ResendOTPSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        # Rate limiting: max 3 resends per day
        cache_key = f"otp_resend_{email}"
        resend_count = cache.get(cache_key, 0)
        
        if resend_count >= 3:
            # Log rate limit exceeded
            log_security_event(
                event="OTP resend rate limit exceeded",
                ip_address=request.META.get('REMOTE_ADDR'),
                extra_data={"email": email, "resend_count": resend_count}
            )
            return Response({
                'message': 'Maximum OTP resend attempts reached. Please try again tomorrow.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Create and send new OTP
        from .models import User
        user = User.objects.get(email=email)
        otp = create_otp_for_user(user)
        
        if otp:
            # Increment resend count
            cache.set(cache_key, resend_count + 1, 86400)  # 24 hours
            
            # Log successful OTP resend
            log_user_action(
                action="OTP_RESEND",
                user_id=user.id,
                user_email=user.email,
                success=True,
                extra_data={"ip_address": request.META.get('REMOTE_ADDR'), "resend_count": resend_count + 1}
            )
            
            return Response({
                'message': 'OTP sent successfully. Please check your email.'
            })
        else:
            # Log failed OTP resend
            log_user_action(
                action="OTP_RESEND",
                user_id=user.id,
                user_email=user.email,
                success=False,
                extra_data={"ip_address": request.META.get('REMOTE_ADDR'), "error": "Failed to create OTP"}
            )
            return Response({
                'message': 'Failed to send OTP. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # Log failed OTP resend attempt
        email = request.data.get('email', 'unknown')
        log_security_event(
            event="Failed OTP resend attempt",
            ip_address=request.META.get('REMOTE_ADDR'),
            extra_data={"email": email, "errors": serializer.errors}
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
