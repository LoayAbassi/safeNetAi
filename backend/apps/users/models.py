from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  
import random

def generate_account_number():
    return str(random.randint(10000000, 99999999))


class User(AbstractUser):
    ROLE_CLIENT = "CLIENT"
    ROLE_ADMIN = "ADMIN"
    role = models.CharField(max_length=10, choices=[(ROLE_CLIENT, ROLE_CLIENT),(ROLE_ADMIN, ROLE_ADMIN)], default=ROLE_CLIENT)

