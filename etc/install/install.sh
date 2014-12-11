#!/bin/bash

# Script to set up a Django project on Vagrant.

# Print commands
set -x

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME

PGSQL_VERSION=9.3

# Install essential packages from Apt
sudo apt-get update -y

# Install PIP
sudo apt-get install -y python-pip
sudo apt-get install -y python3-pip

# Postgresql
if ! command -v psql; then
    sudo apt-get install -y postgresql-$PGSQL_VERSION libpq-dev
    sudo cp $PROJECT_DIR/etc/install/pg_hba.conf /etc/postgresql/$PGSQL_VERSION/main/
    sudo /etc/init.d/postgresql reload
fi

# postgresql setup for project
createdb -Upostgres $DB_NAME

# Install libspotify

sudo apt-get install -y build-essential python-dev wget

# from http://pyspotify.mopidy.com/en/latest/installation/
wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/mopidy.list
sudo apt-get update
sudo apt-get install -y libspotify-dev

# from http://stackoverflow.com/questions/21158317/ioerror-on-production-server
sudo apt-get install libffi-dev

# Install RabbitMQ
sudo apt-get install -y rabbitmq-server

# Install and configure virtualenvwrapper
sudo pip install virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$PROJECT_DIR
source `which virtualenvwrapper.sh`
mkvirtualenv $VIRTUALENV_NAME -p `which python3`

cp $PROJECT_DIR/etc/install/bashrc ~/.bashrc
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
echo "export PROJECT_HOME=$PROJECT_DIR" >> ~/.bashrc
echo "source `which virtualenvwrapper.sh`" >> ~/.bashrc

# Change to the project directory
cd $PROJECT_DIR
workon $VIRTUALENV_NAME

# Install the requirements
pip install -r requirements.txt

# Install bower, git, and javascript dependencies
sudo npm install -g bower
sudo apt-get install -y git
bower install --config.interactive=false

# Install the project locally
./setup.py develop

# Django project setup
./manage.py syncdb --noinput
