celery worker --app=app --loglevel=INFO &
gunicorn --workers=2 --bind=0.0.0.0:5000 app:flask_app
