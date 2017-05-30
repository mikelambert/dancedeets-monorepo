PATH=$PATH:/nodejs/bin NODE_ENV=production NODE_PATH=node_server/node_modules/ npm start &
if [ "$DEBUG_MEMORY_LEAKS_GUNICORN" != "" ]; then
  CONF=gunicorn-debug_memory_leaks.conf.py
else
  CONF=gunicorn.conf.py
fi
/env/bin/gunicorn -b :8080 vmruntime.wsgi:meta_app --log-file=- -c $CONF
