from django.db import models

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('transfer', 'Transfer'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('flagged', 'Flagged for Fraud'),
        ('blocked', 'Blocked'),
    )

    transaction_id = models.UUIDField(primary_key=True)
    user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    source_account = models.CharField(max_length=50)
    destination_account = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fraud_score = models.FloatField(null=True)
    triggered_rules = models.JSONField(default=list)

    class Meta:
        ordering = ['-timestamp']
