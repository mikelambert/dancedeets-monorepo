# This runs inside the /app/ directory in the Docker container
# Due to python-compat-multicore running: WORKDIR /app/ .

PATH=$PATH:/nodejs/bin NODE_ENV=production NODE_PATH=node_server/node_modules/ npm start &


# Copied in top-level Dockerfile: ADD . /app/
# And runs in daemon mode
nginx -c /app/nginx.conf


# Both of /app/gunicorn*.py are guaranteed to exist
if [ "$DEBUG_MEMORY_LEAKS_GUNICORN" != "" ]; then
  # Copied in top-level Dockerfile: ADD . /app/
  CONF=gunicorn-debug_memory_leaks.conf.py # from mirroring . into /app/
else
  # Copied in python-compat-multicore: ADD resources/gunicorn.conf.py /app/gunicorn.conf.py
  CONF=gunicorn.conf.py # from python-compat-multicore into /app
fi
# And of course, run our actual python appserver now too.
/env/bin/gunicorn -b :8085 vmruntime.wsgi:meta_app --log-file=- -c $CONF
