#!/bin/sh

echo "Waiting for database..."
while ! nc -z db 5432; do   
  sleep 1
done
echo "Database is ready!"

python manage.py migrate

# run server
exec "$@"
