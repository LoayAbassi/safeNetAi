from rest_framework import serializers
from .models import Transaction, FraudAlert
from apps.risk.models import ClientProfile

class TransactionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_email = serializers.EmailField(source='client.user.email', read_only=True)
    from_account = serializers.CharField(source='client.bank_account_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'client', 'client_name', 'client_email', 'amount', 'transaction_type',
                 'from_account', 'to_account_number', 'status', 'device_fingerprint',
                 'location_lat', 'location_lng', 'created_at']
        read_only_fields = ['client', 'status', 'created_at']

class CreateTransactionSerializer(serializers.ModelSerializer):
    current_location = serializers.JSONField(required=False)
    
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'to_account_number', 'device_fingerprint', 'current_location']
    
    def validate(self, attrs):
        user = self.context['request'].user
        try:
            client_profile = ClientProfile.objects.get(user=user)
        except ClientProfile.DoesNotExist:
            raise serializers.ValidationError("Client profile not found")
        
        # Validate funds for transfer
        if attrs['transaction_type'] == 'transfer':
            if client_profile.balance < attrs['amount']:
                raise serializers.ValidationError("Insufficient funds")
        
        # Extract location from current_location
        current_location = attrs.pop('current_location', {})
        if current_location:
            attrs['location_lat'] = current_location.get('lat')
            attrs['location_lng'] = current_location.get('lng')
        
        attrs['client'] = client_profile
        
        return attrs

class AdminTransactionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_email = serializers.EmailField(source='client.user.email', read_only=True)
    from_account = serializers.CharField(source='client.bank_account_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'client', 'client_name', 'client_email', 'amount', 'transaction_type',
                 'from_account', 'to_account_number', 'status', 'device_fingerprint',
                 'location_lat', 'location_lng', 'created_at']

class FraudAlertSerializer(serializers.ModelSerializer):
    transaction_details = TransactionSerializer(source='transaction', read_only=True)
    
    class Meta:
        model = FraudAlert
        fields = ['id', 'transaction', 'transaction_details', 'risk_score', 'level', 
                 'triggers', 'status', 'created_at']
        read_only_fields = ['transaction', 'risk_score', 'level', 'triggers', 'created_at']

class AdminFraudAlertSerializer(serializers.ModelSerializer):
    transaction_details = AdminTransactionSerializer(source='transaction', read_only=True)
    
    class Meta:
        model = FraudAlert
        fields = ['id', 'transaction', 'transaction_details', 'risk_score', 'level', 
                 'triggers', 'status', 'created_at']
        read_only_fields = ['transaction', 'risk_score', 'level', 'triggers', 'created_at']
