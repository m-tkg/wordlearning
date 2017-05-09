#!/bin/sh

ROOTDIR=$(cd $(dirname $0) && pwd)
test ! -r $ROOTDIR/config.file && exit 200
. $ROOTDIR/config.file

cd $ROOTDIR

SUFFIX=run
docker ps -a | grep -q ${IMAGE_NAME}-${SUFFIX} && docker rm -f ${IMAGE_NAME}-${SUFFIX} || true
