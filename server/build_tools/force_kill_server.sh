#!/bin/bash
ps aux | grep app-devserver.yaml | grep -v grep | awk '{print $2}' | xargs kill -9
