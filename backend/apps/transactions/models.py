from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.risk.models import ClientProfile
from decimal import Decimal

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('transfer', 'Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='transfer')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    to_account_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    risk_score = models.IntegerField(default=0)
    device_fingerprint = models.CharField(max_length=255, blank=True, null=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transfer - {self.amount} DZD - {self.status}"

class TransactionOTP(models.Model):
    """OTP model for transaction verification"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='otps')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Transaction OTP for {self.user.email} - Transaction #{self.transaction.id}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired() and self.attempts < 3
    
    def increment_attempts(self):
        self.attempts += 1
        self.save()
    
    def mark_used(self):
        self.used = True
        self.save()
    
    class Meta:
        ordering = ['-created_at']

class FraudAlert(models.Model):
    LEVEL_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Reviewed', 'Reviewed'),
        ('Resolved', 'Resolved'),
    ]
    
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='fraud_alert')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    risk_score = models.IntegerField()
    triggers = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Fraud Alert - {self.level} - Transaction #{self.transaction.id}"
