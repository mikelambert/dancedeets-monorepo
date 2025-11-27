#!/bin/bash
# Entrypoint script for DanceDeets on GAE Flexible Environment
# Starts both the Node.js render server (for SSR) and gunicorn (Python app)

set -e

# Ensure we're in the app directory
cd /app

# Log startup info to stderr (which GAE Flex captures)
echo "[ENTRYPOINT] Current directory: $(pwd)" >&2
echo "[ENTRYPOINT] Node version: $(node --version 2>&1 || echo 'node not found')" >&2
echo "[ENTRYPOINT] Files in dist/js-server:" >&2
ls -la /app/dist/js-server/*.js 2>&1 | head -5 >&2

# Create a log file for Node.js render server
RENDER_LOG="/tmp/render-server.log"

# Start the Node.js render server in the background
# Redirect both stdout and stderr to log file and also to stderr for Cloud Logging
echo "[ENTRYPOINT] Starting Node.js render server on port 8090..." >&2
node /app/dist/js-server/renderServer.js > >(tee -a "$RENDER_LOG" >&2) 2>&1 &
RENDER_SERVER_PID=$!

# Give the render server a moment to start up
sleep 5

# Check if render server is running
if ! kill -0 $RENDER_SERVER_PID 2>/dev/null; then
    echo "[ENTRYPOINT] ERROR: Node.js render server failed to start (PID: $RENDER_SERVER_PID)." >&2
    echo "[ENTRYPOINT] Render server log contents:" >&2
    cat "$RENDER_LOG" >&2 || echo "[ENTRYPOINT] No log file found" >&2
else
    echo "[ENTRYPOINT] Node.js render server started successfully (PID: $RENDER_SERVER_PID)" >&2
    # Test the render server
    echo "[ENTRYPOINT] Testing render server..." >&2
    curl -s -X POST http://localhost:8090/render -H "Content-Type: application/json" -d '{"path": "/app/dist/js-server/tutorialCategory.js", "serializedProps": "{}", "toStaticMarkup": false}' 2>&1 | head -c 200 >&2 || echo "[ENTRYPOINT] curl test failed" >&2
    echo "" >&2
fi

# Start gunicorn as the main process (this keeps the container alive)
echo "[ENTRYPOINT] Starting gunicorn on port 8080..." >&2
exec gunicorn -c gunicorn.conf.py main:app
