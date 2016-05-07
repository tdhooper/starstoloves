dropdb starstoloves -U postgres
createdb -Upostgres starstoloves
./manage.py syncdb --noinput
./manage.py migrate