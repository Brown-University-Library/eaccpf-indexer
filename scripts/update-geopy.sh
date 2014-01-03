#!/bin/bash
# update the geopy module

# Absolute path to this script. /home/user/bin/foo.sh
SCRIPT=$(readlink -f $0)

# Absolute path this script is in. /home/user/bin
SCRIPTPATH=`dirname $SCRIPT`

# absolute path to the project folder
PROJECT=`dirname $SCRIPTPATH`

TEMP="$PROJECT/temp"
REPO="$TEMP/geopy"

# -----------------------------------------------------------------------------
# get the latest copy of eaccpf-ajax

if [ ! -d "$TEMP" ]; then
  mkdir $TEMP
fi

if [ ! -d "$REPO" ]; then
  cd $TEMP
  git clone https://github.com/geopy/geopy.git
fi

echo "Updating local geopy repo"
cd $REPO
git pull origin master

# -----------------------------------------------------------------------------
# deploy components into the application folder

echo "Updating geopy component"

rm -fr $PROJECT/Indexer/geopy
cp -a $REPO/geopy $PROJECT/Indexer/geopy

cd $SCRIPTPATH
