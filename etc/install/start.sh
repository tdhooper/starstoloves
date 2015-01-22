# Print commands
set -x

PROJECT_NAME=$1
VIRTUALENV_NAME=$PROJECT_NAME
PROJECT_DIR=/home/vagrant/$PROJECT_NAME


# Kill and restart screen
screen -S "djangoServer" -X quit
screen -dmS "djangoServer"

screen -S "celeryWorker" -X quit
screen -dmS "celeryWorker"

sleep 5

# Start the Django development server in screen

# Use virtual environment
screen -S "djangoServer" -p 0 -X stuff "cd $PROJECT_DIR && workon $VIRTUALENV_NAME
"
# Start python server
screen -S "djangoServer" -p 0 -X stuff "python ./manage.py runserver 0.0.0.0:8000
"

# Start the Celery worker process in screen

# Use virtual environment
screen -S "celeryWorker" -p 0 -X stuff "cd $PROJECT_DIR && workon $VIRTUALENV_NAME
"
# Start python server
screen -S "celeryWorker" -p 0 -X stuff "celery -A starstoloves worker -l info
"

echo 'The site should be accessible at http://localhost:8111'