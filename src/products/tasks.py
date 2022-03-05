import os
import csv
from itertools import islice
from celery import shared_task
from .models import Product


@shared_task
def uploadData(file_path):
    reader = csv.reader(open(file_path), delimiter=',', quotechar='"')
    header = next(reader)
    batch_size = 10000
    while True:
        batch = [Product(name=row[0], sku=row[1], description=row[2])
                 for row in islice(reader, batch_size)]
        if not batch:
            break
        Product.objects.bulk_create(batch, batch_size, ignore_conflicts=True)
    print(batch_size)
    
    os.remove(file_path)
