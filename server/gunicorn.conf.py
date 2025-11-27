# Gunicorn configuration for DanceDeets on App Engine Flexible Environment

import multiprocessing
import os

# Bind to port 8080 (standard GAE Flexible Environment port)
bind = "0.0.0.0:8080"

# Worker configuration
# Use gthread worker for better concurrency with I/O-bound workloads
worker_class = "gthread"

# Number of workers - based on CPU cores
# For App Engine Flexible, typically 1 CPU = 2-4 workers is a good balance
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Threads per worker
# For I/O-bound applications (database, API calls), more threads help
threads = int(os.environ.get("GUNICORN_THREADS", 4))

# Maximum concurrent requests
# workers * threads = max concurrent requests
# Example: 3 workers * 4 threads = 12 concurrent requests

# Timeout settings
timeout = 60  # Worker timeout in seconds
graceful_timeout = 30  # Graceful worker restart timeout
keepalive = 5  # Keepalive connections

# Request handling
max_requests = 1000  # Restart workers after this many requests (helps with memory leaks)
max_requests_jitter = 100  # Add randomness to prevent all workers restarting at once

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server mechanics
daemon = False  # Don't daemonize (App Engine manages the process)
pidfile = None
user = None
group = None
umask = 0

# Process naming
proc_name = "dancedeets"

# Preload app for faster worker startup (but uses more memory)
preload_app = False

# Forward proxy headers (X-Forwarded-For, X-Forwarded-Proto, etc.)
forwarded_allow_ips = "*"
proxy_allow_ips = "*"

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    pass

def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    pass

def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    pass
