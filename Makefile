run:
	python manage.py runserver
migrate:
	python manage.py migrate
migrations:
	python manage.py makemigrations
superuser:
	python manage.py createsuperuser
req:
	pip freeze > requirements.txt
static:
	python manage.py collectstatic
up: 
	railway up 