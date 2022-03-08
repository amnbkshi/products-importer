# Products Importer

Django project which allows to upload products data into database from a csv file. These products can further be interacted with various REST APIs.

## Installation
### Prerequisites:
- `Postgres 12.0+`
- `Python 3.8+`
- `Redis 3.0+`

### Project Setup:
- Clone the project
```
git clone https://github.com/amnbkshi/products-importer.git
```
- Create virtual environment and activate
```
virtualenv -p python3.8 api/venv
source ./venv/bin/activate
```
- Install dependencies
```
pip install -r requirements.txt
```
- Rename the `.sample-env` file to `.env` and add the respective entries
- Setup django project
```
cd src
./manage.py migrate
# Generate user which will be used for login
./manage.py createsuperuser
```
- Run the project
```
# django
./manage.py runserver
# celery
celery -A core worker -l info
```
## Functionality
### Upload feature
- The `upload_csv/` endpoint accepts a `POST` request with the csv file as form body.
- The CSV file is temporarily stored into the disk after which an async celery task if triggered to update the database.
- The celery task updates the db in batches using `bulk_create` as it reduces the db connections
```
Product.objects.bulk_create(batch, batch_size, ignore_conflicts=True)
```
> Here `ignore_conflict=True` is used to ignore the duplicate entries
- The api returns celery `task_id` which is used to track the progress of upload.

### Progress tracking
- Using the `task_id` from above api, execute the following command in terminal
```
curl -XPOST --no-buffer http://127.0.0.1:8000/status/ --data-raw '{"task_id": "Enter the task_id value here"}'
```
> Postman was not behaving correctly with SSEs hence using cURL here.
- The above command initiates connection with the backend SSE consumer which sends progress updates until the upload is finished.
- To calculate progress, the celery upload task keeps on saving the current batch_size in its message backend (i.e. `redis`) which the consumer reads and sends to client.

### CRUD 
- All CRUD functionalities are exposed on the `products/` endpoint via Django Rest Framework.
> - Have used DRF here as the APIs only required basic CRUD operations and DRF offers those out of the box.
> - The APIs require BasicAuthentication with the username and password of the superuser created above.
- `delete_all/` is also available to remove all entries from the Products table.
> This is carried out under the `@transaction.atomic` decorator to maintain reliability in the database operations.
### Webhooks
- Webhooks can be configured using the `webhooks/` endpoint.
- Django `post_save` signal is used to trigger a celery task which calls webhooks whenever an object is created or updated.
- Doing this with an async task to improve application performance.
## Improvements
- To upload the csv I am storing it on disk which makes the overall task a bit slower. The file can be stored on an in-memory store with larger memory to improve speed and scalability of the application.
- The implementation of SSE with django channels is a bit hackish. Also, lack of proper frontend client makes it even more trickier to use websockets. Library implementations (`django-eventstream`) can be used to make the implementation a bit more cleaner.
- I have not indexed the columns on SKU/name, but if the filtering feature is frequently used, indexes can be added to improve read time of the application.
- Note to be made, this will increase the write time of our operations and may become a bottleneck when size starts to grow. Sharding / separate indexing cluster (elasticsearch) can be explored to tackle these.
- Have not added test cases to the project. Both unit and integration tests can be added to improve the overall quality of codebase.
