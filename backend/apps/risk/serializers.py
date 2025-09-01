from rest_framework import serializers
from .models import Rule, Threshold

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ['id', 'key', 'description', 'enabled', 'params']

class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = ['id', 'key', 'value', 'description']
