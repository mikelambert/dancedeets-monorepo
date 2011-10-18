#!/usr/bin/bash

nosetests --exclude="mapreduce|gdata|atom" $1 $2 $3 $4 $5
