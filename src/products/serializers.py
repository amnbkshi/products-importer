from rest_framework import serializers
from .models import Product, Webhooks


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class WebhooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhooks
        fields = "__all__"