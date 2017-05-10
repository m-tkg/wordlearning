#!/bin/sh

ROOTDIR=$(cd $(dirname $0) && pwd)
test ! -r $ROOTDIR/config.file && exit 200
. $ROOTDIR/config.file

cd $ROOTDIR

docker ps -a | grep -q ${IMAGE_LOCAL}-work && docker rm ${IMAGE_LOCAL}-work || true
docker images | grep -q ${IMAGE_LOCAL} && docker rmi ${IMAGE_LOCAL} || true
docker build -t ${IMAGE_LOCAL} $@ ./
