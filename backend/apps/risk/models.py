from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import random

def generate_random_8digit():
    """Generate a unique 8-digit bank account number"""
    while True:
        account_number = str(random.randint(10000000, 99999999))
        # Check if this account number already exists
        if not ClientProfile.objects.filter(bank_account_number=account_number).exists():
            return account_number

class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, unique=True, default=generate_random_8digit)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="Balance in Algerian Dinar (DZD)")
    device_fingerprint = models.CharField(max_length=255, blank=True, null=True)
    home_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    home_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_known_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_known_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    avg_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="Average transaction amount in DZD")
    std_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="Standard deviation of transaction amounts in DZD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """Validate that national_id is unique"""
        if self.national_id:
            existing_profile = ClientProfile.objects.filter(national_id=self.national_id)
            if self.pk:
                existing_profile = existing_profile.exclude(pk=self.pk)
            if existing_profile.exists():
                raise ValidationError({'national_id': 'A client profile with this National ID already exists.'})

    def save(self, *args, **kwargs):
        # Generate account number if not provided
        if not self.bank_account_number:
            self.bank_account_number = generate_random_8digit()
        
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

class Rule(models.Model):
    """
    Fraud detection rules that can be configured by admins
    """
    key = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    params = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.key} - {'Enabled' if self.enabled else 'Disabled'}"

class Threshold(models.Model):
    """
    Configurable thresholds for fraud detection
    """
    key = models.CharField(max_length=64, unique=True)
    value = models.FloatField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    class Meta:
        verbose_name = "Threshold"
        verbose_name_plural = "Thresholds"
