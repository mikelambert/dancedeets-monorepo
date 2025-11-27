#!/bin/bash
# DanceDeets startup script for App Engine Flexible Environment
# This runs inside the /app/ directory in the Docker container
# Starts: Node.js render server, nginx reverse proxy, and Python gunicorn server

set -e

cd /app

echo "Starting DanceDeets services..."

# Start Node.js render server in background
# The render server handles React SSR and MJML email rendering
echo "Starting Node.js render server..."
NODE_ENV=production NODE_PATH=node_server/node_modules/ npm start &

# Give Node.js a moment to start
sleep 2

# Start nginx in daemon mode as reverse proxy
# nginx listens on port 8080 (App Engine expected port) and proxies to gunicorn on 8085
echo "Starting nginx..."
nginx -c /app/nginx.conf

# Determine gunicorn config
if [ "$DEBUG_MEMORY_LEAKS_GUNICORN" != "" ]; then
  CONF=/app/gunicorn-debug_memory_leaks.conf.py
else
  CONF=/app/gunicorn.conf.py
fi

# Check if config file exists, use defaults if not
if [ ! -f "$CONF" ]; then
  echo "Gunicorn config not found at $CONF, using defaults"
  CONF=""
fi

# Start gunicorn with the Flask application
# Gunicorn listens on port 8085, nginx proxies requests to it
echo "Starting gunicorn..."
if [ -n "$CONF" ]; then
  exec gunicorn -b :8085 main:application --log-file=- -c $CONF
else
  exec gunicorn -b :8085 main:application --log-file=- \
    --workers=2 \
    --threads=4 \
    --worker-class=gthread \
    --timeout=60 \
    --graceful-timeout=30 \
    --keep-alive=5
fi
