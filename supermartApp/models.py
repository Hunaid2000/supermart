from django.db import models
from django import forms

class Account(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)
    is_seller= models.BooleanField(default=False)
