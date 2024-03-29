#!/bin/bash

# Update and install required packages
sudo apt update
sudo apt install -y python3 python3-pip python3-dev libpq-dev postgresql postgresql-contrib

# Create PostgreSQL database and user
sudo -u postgres psql -c "CREATE DATABASE db_proj;"
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin';"
sudo -u postgres psql -c "ALTER ROLE admin SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE admin SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE admin SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE db_proj TO admin;"
 

# Install virtualenv and create a virtual environment
pip3 install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
sudo mkdir static

# Install project dependencies
pip3 install -r requirements.txt

# Run Django management commands
python3 manage.py makemigrations 
python3 manage.py migrate 
python3 manage.py createsuperuser 

