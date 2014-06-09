#!/bin/sh
cd lettera
rm db.sqlite3
echo 'python manage.py syncdb'
python manage.py syncdb || exit
echo 'python manage.py loaddata datas'
python manage.py loaddata datas || exit
echo 'python manage.py initdb'
python manage.py initdb || exit
echo 'python manage.py runserver'
python manage.py runserver || exit
