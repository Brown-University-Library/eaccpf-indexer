#!/bin/bash
# this script will run the full package test suite and test coverage analysis
# if you execute this script with the 'source' command, it won't be able to 
# locate the script path correctly. Instead set the script file to be 
# executable by your user, and then run it directly.

# Absolute path to this script. /home/user/bin/foo.sh
SCRIPT=$(readlink -f $0)

# Absolute path this script is in. /home/user/bin
SCRIPTPATH=`dirname $SCRIPT`

# absolute path to the project folder
PROJECT=`dirname $SCRIPTPATH`

# set the python path so that python knows where to find our application 
# modules
export PYTHONPATH=$PROJECT/Indexer

# run unit tests
echo $PROJECT
nosetests $PROJECT/Indexer

