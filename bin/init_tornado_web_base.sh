#!/bin/bash

# ----------------------------------------
# DESCRIPTION
#
# ----------------------------------------
set -e	# or use "set -o errexit" to quit on error.
set -x  # or use "set -o xtrace" to print the statement before you execute it.

CUR_FILE_DIR=$(cd "$(dirname "$0")"; pwd)
RUNNING_DIR=$(pwd)
cp -R $CUR_FILE_DIR/../src $RUNNING_DIR/src
ln -nfs /Users/zhongwei/life/tornado/tornado $RUNNING_DIR/src/tornado

