#!/bin/sh

ROOTDIR=$(cd $(dirname $0) && pwd)
test ! -r $ROOTDIR/config.file && exit 200
. $ROOTDIR/config.file

cd $ROOTDIR

SUFFIX=run
OPTION=""
echo launch local image.
IMAGE=${IMAGE_LOCAL}

docker ps -a | grep -q ${IMAGE_NAME}-${SUFFIX} && docker rm -f ${IMAGE_NAME}-${SUFFIX} || true
docker run --cap-add=ALL -p 8080:80 -v ${HOME}/work/docker/english/project:/root/project -d -P -h ${IMAGE_NAME}-${SUFFIX} --name ${IMAGE_NAME}-${SUFFIX} ${IMAGE}
