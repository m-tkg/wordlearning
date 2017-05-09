#!/bin/sh

ROOTDIR=$(cd $(dirname $0) && pwd)
test ! -r $ROOTDIR/config.file && exit 200
. $ROOTDIR/config.file

cd $ROOTDIR

SUFFIX=run

docker exec -it ${IMAGE_NAME}-${SUFFIX} su
