celery worker --app=app --loglevel=INFO &
gunicorn --workers=2 --bind=0.0.0.0:8000 app:flask_app
