from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

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
    class Meta:
        model = User
        fields = ("username","email","password","role")
    def create(self, validated):
        user = User(username=validated["username"], email=validated.get("email"), role=validated.get("role","CLIENT"))
        user.set_password(validated["password"])
        user.save()
        return user
