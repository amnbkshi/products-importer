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
git clone https://github.com/aasaanjobs/api.git
```
- Create virtual environment and activate
```
virtualenv -p python3.8 api/venv
source api/venv/bin/activate
```
- Install dependencies
```
pip install -r api/requirements/base.txt
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

## Improvements
