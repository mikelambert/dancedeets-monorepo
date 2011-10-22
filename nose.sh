#!/usr/bin/bash

nosetests --with-gae --exclude="mapreduce|gdata|atom" $1 $2 $3 $4 $5
