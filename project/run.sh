#!/bin/sh

ROOTDIR=$(cd $(dirname $0) && pwd)
python ${ROOTDIR}/wordlearning/manage.py makemigrations
python ${ROOTDIR}/wordlearning/manage.py migrate
python ${ROOTDIR}/wordlearning/manage.py runserver 0.0.0.0:8080
