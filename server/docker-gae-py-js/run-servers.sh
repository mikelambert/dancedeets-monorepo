NODE_PATH=node_server/node_modules/ npm start &
#/usr/bin/python2.7 /home/vmagent/python_vm_runtime/vmboot.py
/env/bin/gunicorn -b :8080 vmruntime.wsgi:meta_app --log-file=- -c gunicorn.conf.py
