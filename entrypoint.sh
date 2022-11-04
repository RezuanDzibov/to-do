#!/bin/sh

  while ! nc -z db 5432; do
    sleep 0.1
  done

bash -c "cd app && python manage.py flush --no-input"
bash -c "cd app && python manage.py makemigrations"
bash -c "cd app && python manage.py migrate"
bash -c "cd app && python manage.py loaddata admin_fixture.json --app auth"
exec "$@"