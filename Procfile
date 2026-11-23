release: python manage.py migrate --noinput && python manage.py seed_content && python manage.py purge_rooms
web: gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2