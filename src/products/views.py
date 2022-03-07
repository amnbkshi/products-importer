import os
from django.conf import settings
from django.core.files.base import ContentFile

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
        total_lines = 0
        with open(temp_file_path, 'wb+') as fout:
            file_content = ContentFile(csv_file.read())
            
            for chunk in file_content.chunks():
                total_lines += chunk.count(b'\n')
                fout.write(chunk)

        a = uploadData.delay(temp_file_path)

        curl_command = \
         "curl -XPOST --no-buffer http://127.0.0.1:8000/status/ --data-raw '{{\"task_id\": \"{0}\" }}'"\
         .format(str(a.id))
        
        return Response(data=curl_command, status=status.HTTP_202_ACCEPTED)


class ListCreateProducts(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'sku', 'status']


class RetrieveUpdateDestroyProducts(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DeleteAllProducts(APIView):

    def delete(self, request):
        Product.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCreateWebhooks(ListCreateAPIView):
    queryset = Webhooks.objects.all()
    serializer_class = WebhooksSerializer
