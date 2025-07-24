from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
        ('regular_user', 'Regular User'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES, default='regular_user')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
