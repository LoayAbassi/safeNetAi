from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, EmailOTP
from apps.risk.models import ClientProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    national_id = serializers.CharField(max_length=20)
    bank_account_number = serializers.CharField(max_length=20)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 
                 'national_id', 'bank_account_number']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if user already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("User with this email already exists")
        
        # Validate client profile exists and matches
        try:
            profile = ClientProfile.objects.get(
                national_id=attrs['national_id'],
                bank_account_number=attrs['bank_account_number']
            )
            
            # Check if names match (case-insensitive)
            if (profile.first_name.lower() != attrs['first_name'].lower() or 
                profile.last_name.lower() != attrs['last_name'].lower()):
                raise serializers.ValidationError("Account verification failed. Contact admin.")
            
            # Check if profile is already linked to a user
            if profile.user is not None:
                raise serializers.ValidationError("Account verification failed. Contact admin.")
                
        except ClientProfile.DoesNotExist:
            raise serializers.ValidationError("Account verification failed. Contact admin.")
        
        return attrs
    
    def create(self, validated_data):
        # Remove extra fields
        validated_data.pop('password_confirm')
        validated_data.pop('national_id')
        validated_data.pop('bank_account_number')
        
        # Create user with email verification required
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_email_verified=False
        )
        
        return user

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        if user.is_email_verified:
            raise serializers.ValidationError("Email already verified")
        
        # Check OTP
        try:
            otp_obj = EmailOTP.objects.get(
                user=user,
                otp=attrs['otp'],
                used=False
            )
            
            if otp_obj.is_expired():
                raise serializers.ValidationError("OTP has expired")
            
            if not otp_obj.is_valid():
                raise serializers.ValidationError("Invalid OTP")
                
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")
        
        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        return attrs

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.is_email_verified:
                raise serializers.ValidationError("Email already verified")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_email_verified:
            raise serializers.ValidationError("Email not verified. Please verify your email first.")
        
        attrs['user'] = user
        return attrs

class ClientProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'user_email', 'first_name', 'last_name', 'full_name',
                 'national_id', 'bank_account_number', 'balance', 'device_fingerprint',
                 'home_lat', 'home_lng', 'last_known_lat', 'last_known_lng',
                 'avg_amount', 'std_amount', 'created_at', 'updated_at']
        read_only_fields = ['user', 'bank_account_number', 'avg_amount', 'std_amount', 
                           'created_at', 'updated_at']

class AdminClientProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'user_email', 'first_name', 'last_name', 'full_name',
                 'national_id', 'bank_account_number', 'balance', 'device_fingerprint',
                 'home_lat', 'home_lng', 'last_known_lat', 'last_known_lng',
                 'avg_amount', 'std_amount', 'created_at', 'updated_at']
        read_only_fields = ['bank_account_number', 'avg_amount', 'std_amount', 
                           'created_at', 'updated_at']
