from rest_framework import serializers
from .models import Threshold, Rule
from apps.transactions.models import Transaction, FraudAlert
from apps.users.models import ClientProfile

class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = ["id", "key", "value", "description"]

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ["id", "key", "description", "enabled", "params_json"]

class ClientProfileAdminSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = ['id', 'full_name', 'national_id', 'bank_account_number', 'balance', 'risk_score', 'user_username', 'user_email', 'created_at']

class TransactionAdminSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_national_id = serializers.CharField(source='client.national_id', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'client_name', 'client_national_id', 'amount', 'transaction_type', 'timestamp']

class FraudAlertAdminSerializer(serializers.ModelSerializer):
    transaction_details = TransactionAdminSerializer(source='transaction', read_only=True)
    
    class Meta:
        model = FraudAlert
        fields = ['id', 'transaction_details', 'risk_level', 'message', 'status', 'created_at']
