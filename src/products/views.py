import os
from django.conf import settings
from django.core.files.base import ContentFile

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .tasks import UploadFromCSVTask



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

        temp_file_path = os.path.join(settings.BASE_DIR + "tempstore" + csv_file.name)

        with open(temp_file_path, 'wb+') as fout:
            file_content = ContentFile(csv_file.read())
            for chunk in file_content.chunks():
                fout.write(chunk)

        UploadFromCSVTask(temp_file_path)

        return Response(data="File uploading", status=status.HTTP_202_ACCEPTED)
