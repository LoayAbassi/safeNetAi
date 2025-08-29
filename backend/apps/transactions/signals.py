from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction
from apps.risk.engine import FraudDetectionEngine

@receiver(post_save, sender=Transaction)
def detect_fraud_on_transaction(sender, instance, created, **kwargs):
    """
    Automatically detect fraud when a transaction is created
    """
    if created:
        engine = FraudDetectionEngine()
        risk_level, message, risk_score = engine.detect_fraud(instance)
        
        # Create fraud alert if risk is detected
        if risk_level in ['Medium', 'High']:
            engine.create_fraud_alert(instance, risk_level, message)
        
        # Update client's risk score
        instance.client.risk_score = max(instance.client.risk_score, risk_score)
        instance.client.save(update_fields=['risk_score'])
