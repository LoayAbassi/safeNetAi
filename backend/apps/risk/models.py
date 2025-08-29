from django.db import models
from django.conf import settings

class Rule(models.Model):
    """
    Fraud detection rules that can be configured by admins
    """
    key = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    params_json = models.JSONField(default=dict)
    
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
