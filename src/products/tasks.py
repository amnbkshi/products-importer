import os
import csv
from itertools import islice
from celery import shared_task, current_task
from .models import Product


@shared_task
def uploadData(file_path):
    with open(file_path, "r") as f:
        reader = csv.reader(f, delimiter = ",", quotechar='"')
        total_lines = sum(1 for row in reader)
    
    reader = csv.reader(open(file_path), delimiter=',', quotechar='"')
    header = next(reader)
    batch_size = 10000
    prog = 0

    while True:
        batch = [Product(name=row[0], sku=row[1], description=row[2])
                 for row in islice(reader, batch_size)]
        if not batch:
            break
        Product.objects.bulk_create(batch, batch_size, ignore_conflicts=True)
        current_task.update_state(state='PROGRESS', meta={'current': prog, 'total': total_lines})
        prog += batch_size
    
    os.remove(file_path)
    return {'current': 100, 'total': 100, }
