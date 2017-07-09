#!/bin/sh

# change directory
APPDIR=/Users/alexandreattia/Desktop/Work/Practice/HackerRankChallenge/TwitterParsing
export APPDIR
cd $APPDIR

# activate virtual env
source /Users/alexandreattia/Desktop/Work/workenv/bin/activate

# launch python script
./download_pics.py