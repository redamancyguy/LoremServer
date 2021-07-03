from django.db import models


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=32, default=None, unique=True)
    password = models.CharField(max_length=128, default=None)
    phone = models.CharField(max_length=16, default=None)
    email = models.CharField(max_length=20, default=None, unique=True)
    emailCode = models.CharField(default=None, max_length=8)
