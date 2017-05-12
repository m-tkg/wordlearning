#!/bin/sh

ROOTDIR=$(cd $(dirname $0) && pwd)
LOGFILE=${ROOTDIR}/wordlearning.log
MAX_RETRY=5

retry() {
  n=0
  until [ $n -ge ${MAX_RETRY} ]
  do
    "${@}" >>${LOGFILE} 2>&1 && break
    n=$(( n + 1 ))
    echo "retrying(${n}/${MAX_RETRY})...: ${@}" >>${LOGFILE} 2>&1
    sleep 1
  done
  if [ $n -ge ${MAX_RETRY} ]; then
    echo "failed: ${@}" >>${LOGFILE} 2>&1
    exit 1
  fi
}

touch ${LOGFILE}
retry pip install -r /requirements.txt
retry python -c 'import nltk; nltk.download("wordnet")'
retry python ${ROOTDIR}/wordlearning/manage.py makemigrations app
retry python ${ROOTDIR}/wordlearning/manage.py migrate
retry python ${ROOTDIR}/wordlearning/manage.py runserver 0.0.0.0:8080
