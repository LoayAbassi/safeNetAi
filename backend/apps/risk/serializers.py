from rest_framework import serializers
from .models import Transaction, Threshold, Rule, Account

class QuoteSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    to_iban = serializers.CharField()
    amount = serializers.FloatField()
    currency = serializers.CharField()
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    device_id = serializers.CharField(required=False)
    ip = serializers.IPAddressField(required=False)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"

class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = ["id","key","value"]

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = "__all__"

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id","iban","currency","balance"]
