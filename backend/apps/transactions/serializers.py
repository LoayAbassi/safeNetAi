from rest_framework import serializers
from .models import Transaction, FraudAlert
from apps.users.serializers import ClientProfileSerializer

class TransactionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'client', 'client_name', 'amount', 'transaction_type', 'timestamp']
        read_only_fields = ['timestamp']

class FraudAlertSerializer(serializers.ModelSerializer):
    transaction_details = TransactionSerializer(source='transaction', read_only=True)
    
    class Meta:
        model = FraudAlert
        fields = ['id', 'transaction', 'transaction_details', 'risk_level', 'message', 'status', 'created_at']
        read_only_fields = ['created_at']

class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
    
    def create(self, validated_data):
        # Get the client profile from the authenticated user
        user = self.context['request'].user
        try:
            client_profile = user.clientprofile
        except:
            raise serializers.ValidationError("No client profile found for this user.")
        
        validated_data['client'] = client_profile
        return super().create(validated_data)
