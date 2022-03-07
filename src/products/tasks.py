import os
import csv
import requests
from itertools import islice
from celery import shared_task, current_task
from .models import Product, Webhooks


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


@shared_task
def callWebhooks(payload):
    """
    Calls all the active webhooks in the system whenever
    Product model is saved using django' post_save' signal
    """
    print(payload)
    clients = Webhooks.objects.filter(is_active=True)
    for client in clients:
        url = client.callback_url
        headers = {"Authorization": "Bearer {0}".format(client.token)}
        res = requests.post(url=url, data=payload, headers=headers)
