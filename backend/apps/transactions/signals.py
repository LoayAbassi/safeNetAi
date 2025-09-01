from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction
from apps.risk.engine import RiskEngine

@receiver(post_save, sender=Transaction)
def detect_fraud_on_transaction(sender, instance, created, **kwargs):
    """
    Automatically detect fraud when a transaction is created
    """
    if created:
        engine = RiskEngine()
        risk_score, triggers, requires_otp, decision = engine.calculate_risk_score(instance)
        
        # Create fraud alert if risk is detected
        if risk_score >= 40:  # Medium or High risk
            engine.create_fraud_alert(instance, risk_score, triggers)
