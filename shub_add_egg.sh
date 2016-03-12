#!/bin/bash
# Does the legwork of building and adding an egg to the server.
# Except just shows the call we would have used (since I don't have shubc installed)
# But at least this gives me something I can easily upload, for now.
set -e
cd $(mktemp -d)
PIP_OUTPUT=$(pip download $1)
TAR_GZ=$(echo $PIP_OUTPUT | grep -o "[^ ]*.tar.gz" | head -1)
tar xzf $TAR_GZ
cd $(dirname $(find . -name 'setup.py'))
BDIST_OUTPUT=$(python setup.py bdist_egg)
BDIST_FILE=$(echo $BDIST_OUTPUT | sed "s/.*creating '\([^']*\)'.*/\1/")
REAL_BDIST_FILE="$(pwd)/$BDIST_FILE"
NAME=$(python setup.py --name)
VERSION=$(python setup.py --version)
echo shubc eggs-add PROJECT_ID "$REAL_BDIST_FILE"  name "$NAME" version "$VERSION"

