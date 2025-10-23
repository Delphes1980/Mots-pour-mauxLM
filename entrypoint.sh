#!/bin/sh

echo "Waiting for database to be available..."

until PGPASSWORD=$DB_PASSWORD psql -h "db" -U "$DB_USER" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - executing command"

export PYTHONPATH=$PYTHONPATH:/app

# Création des tables
python3 /app/app/utils.py db_setup

# Appel du fichier pour créer les prestations
python3 /app/app/seed.py

echo "Starting Gunicorn server..."
exec gunicorn -w 4 -b 0.0.0.0:5000 app.run:app