from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ClientProfile

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data.get("username"), password=data.get("password"))
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("Inactive user")
        data["user"] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    national_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password", "national_id")
    
    def validate_national_id(self, value):
        """Check if a ClientProfile exists with this national_id"""
        try:
            ClientProfile.objects.get(national_id=value)
            return value
        except ClientProfile.DoesNotExist:
            raise serializers.ValidationError("No client profile found with this National ID. Please contact an administrator.")
    
    def create(self, validated_data):
        national_id = validated_data.pop('national_id')
        user = User(
            username=validated_data["username"], 
            email=validated_data.get("email"), 
            role="CLIENT"
        )
        user.set_password(validated_data["password"])
        user.save()
        
        # Link user to existing ClientProfile
        try:
            profile = ClientProfile.objects.get(national_id=national_id)
            profile.user = user
            profile.save()
        except ClientProfile.DoesNotExist:
            pass  # This shouldn't happen due to validation
        
        return user

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['id', 'full_name', 'national_id', 'bank_account_number', 'balance', 'risk_score', 'created_at']
        read_only_fields = ['national_id', 'bank_account_number', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    profile = ClientProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'profile']
