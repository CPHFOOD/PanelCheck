#!/bin/bash
BASEDIR=$(dirname "$0")
PYTHON_PATH=$BASEDIR/Contents/MacOS/python 
SCRIPT=$BASEDIR/Contents/Resources/PanelCheck.py

$($PYTHON_PATH $SCRIPT)