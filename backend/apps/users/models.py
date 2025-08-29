from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  
import random

def generate_account_number():
    return str(random.randint(10000000, 99999999))

def generate_national_id():
    return str(random.randint(100000000, 999999999))

class User(AbstractUser):
    ROLE_CLIENT = "CLIENT"
    ROLE_ADMIN = "ADMIN"
    role = models.CharField(max_length=10, choices=[(ROLE_CLIENT, ROLE_CLIENT),(ROLE_ADMIN, ROLE_ADMIN)], default=ROLE_CLIENT)

class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=20, unique=True, default=generate_national_id)
    bank_account_number = models.CharField(max_length=20, unique=True, default=generate_account_number)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    risk_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

