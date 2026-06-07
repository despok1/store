run:
	python manage.py runserver
migrations:
	python manage.py makemigrations
migrate:
	python manage.py migrate
superuser:
	python manage.py createsuperuser
req:
	pip freeze > requirements.txt
static:
	python manage.py collectstatic
up: 
	railway up 
push:
	git add .
	@if git diff --cached --quiet; then \
		echo "No changes to commit"; \
	else \
		git commit -m "Auto commit"; \
	fi
	git push
ssh:
	railway ssh --project=752af7ac-5ce8-425e-b68e-d018a6486b8b --environment=50df1dbf-608e-403f-8baa-d12903a46cee --service=b188408b-8201-49a3-abbc-846861100cc0