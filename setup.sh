#!/bin/bash

# Update and install required packages
sudo apt update
sudo apt install -y git python3-pip python3-dev libpq-dev postgresql postgresql-contrib

# Create PostgreSQL database and user
sudo -u postgres psql -c "CREATE DATABASE db_proj;"
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin';"
sudo -u postgres psql -c "ALTER ROLE admin SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE admin SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE admin SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE db_proj TO admin;"
 

# Install virtualenv and create a virtual environment
sudo pip3 install virtualenv
python3 -m virtualenv myprojectenv
source myprojectenv/bin/activate

# Install project dependencies
pip install -r requirements.txt

# Run Django management commands
python manage.py makemigrations core_app
python manage.py migrate core_app
python manage.py createsuperuser --username=admin --noinput
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').update(password='admin01')" | python manage.py shell
