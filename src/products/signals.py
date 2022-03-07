import imp
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product
from .serializers import ProductSerializer
from .tasks import callWebhooks

@receiver(post_save, sender=Product)
def call_webhooks(sender, instance, created, **kwargs):
    payload = ProductSerializer(instance).data
    callWebhooks.delay(payload)
