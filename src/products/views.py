import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

from .tasks import uploadData
from .serializers import ProductSerializer, WebhooksSerializer
from .models import Product, Webhooks



class ProductsFromCSView(APIView):
    """
    API to upload data to DB using CSV file 
    Methods Allowed: POST
    Endpoint: upload_csv/
    """

    @staticmethod
    def validate(csv_file):
        if not csv_file:
            raise ValidationError("No file given.")
        if not csv_file.name.split('.')[-1] == "csv":
            raise ValidationError("Only csv files are allowed")

    def post(self, request):
        csv_file = request.FILES['file']
        self.validate(csv_file)

        temp_file_path = os.path.join(settings.BASE_DIR, "tempstore", csv_file.name)
        with open(temp_file_path, 'wb+') as fout:
            file_content = ContentFile(csv_file.read())
            
            for chunk in file_content.chunks():
                fout.write(chunk)

        a = uploadData.delay(temp_file_path)

        return Response(data=str(a.id), status=status.HTTP_202_ACCEPTED)


class ListCreateProducts(ListCreateAPIView):
    """
    API to list all products or create new
    Methods Allowed: GET, POST 
    Endpoint: products/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'sku', 'status']


class RetrieveUpdateDestroyProducts(RetrieveUpdateDestroyAPIView):
    """
    API to retrieve, update or delete a single product using primary key
    Methods Allowed: GET, PATCH, DELETE 
    Endpoint: products/<primary_key>
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DeleteAllProducts(APIView):
    """
    API to delete all products
    Methods Allowed: DELETE
    Endpoint: delete_all/
    """
    @transaction.atomic
    def delete(self, request):
        Product.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCreateWebhooks(ListCreateAPIView):
    """
    API to list all webhooks or create new
    Methods Allowed: GET, POST 
    Endpoint: webhooks/
    """
    queryset = Webhooks.objects.all()
    serializer_class = WebhooksSerializer
