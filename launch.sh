#!/bin/sh
cd lettera
echo 'python manage.py runserver'
python manage.py runserver || exit
