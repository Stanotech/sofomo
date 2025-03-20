#!/bin/sh

echo "Waiting for database..."
until nc -z -v -w30 db 5432; do
  echo "Waiting for database..."
  sleep 1
done
echo "Database is ready!"

echo "Running migrations..."
python manage.py migrate
echo "Migrations completed."

# Running Django server
exec "$@"