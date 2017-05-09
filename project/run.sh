#!/bin/sh

python project/wordlearning/manage.py makemigrations
python project/wordlearning/manage.py migrate
python project/wordlearning/manage.py runserver 0.0.0.0:8080

