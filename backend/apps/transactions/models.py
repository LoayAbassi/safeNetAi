from django.db import models
from django.conf import settings
from apps.users.models import ClientProfile

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    ]
    
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client.full_name} - {self.transaction_type} - {self.amount}"
    
    class Meta:
        ordering = ['-timestamp']

class FraudAlert(models.Model):
    RISK_LEVELS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
    ]
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='fraud_alerts')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Alert for {self.transaction} - {self.risk_level}"
    
    class Meta:
        ordering = ['-created_at']
