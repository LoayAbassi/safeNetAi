from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CLIENT = "CLIENT"
    ROLE_ADMIN = "ADMIN"
    role = models.CharField(max_length=10, choices=[(ROLE_CLIENT, ROLE_CLIENT),(ROLE_ADMIN, ROLE_ADMIN)], default=ROLE_CLIENT)
