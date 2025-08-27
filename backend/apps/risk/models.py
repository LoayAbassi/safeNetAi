import random
from django.db import models
from django.conf import settings

def generate_iban():
    return str(random.randint(1000000000000000, 9999999999999999)) 
class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, blank=True)
    home_lat = models.FloatField(null=True, blank=True)
    home_lng = models.FloatField(null=True, blank=True)
    avg_amount = models.FloatField(default=0)
    std_amount = models.FloatField(default=1)
    last_known_lat = models.FloatField(null=True, blank=True)
    last_known_lng = models.FloatField(null=True, blank=True)
    device_fingerprint_hash = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"

class Account(models.Model):
    owner = models.ForeignKey("ClientProfile", on_delete=models.CASCADE, related_name="accounts")
    iban = models.CharField(max_length=34, unique=True, default=generate_iban)
    currency = models.CharField(max_length=3, default="TND")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.iban}"

        
class Transaction(models.Model):
    STATUS = [(s, s) for s in ["PENDING","ALLOWED","CHALLENGE","BLOCKED","EXECUTED"]]
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    to_iban = models.CharField(max_length=34)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="TND")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS, default="PENDING")
    risk_score = models.IntegerField(default=0)
    decision_reason = models.JSONField(default=list)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    device_id = models.CharField(max_length=128, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

class RiskEvent(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="risk_event")
    signals_json = models.JSONField(default=dict)
    rules_triggered = models.JSONField(default=list)
    decision = models.CharField(max_length=10, choices=[("ALLOW","ALLOW"),("STEP_UP","STEP_UP"),("BLOCK","BLOCK")])
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

class Rule(models.Model):
    key = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    params_json = models.JSONField(default=dict)

class Threshold(models.Model):
    key = models.CharField(max_length=64, unique=True)
    value = models.FloatField()
