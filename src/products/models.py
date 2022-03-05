from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000)
    status = models.BooleanField(default=False)