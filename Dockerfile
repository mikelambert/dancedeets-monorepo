FROM gcr.io/dancedeets-hrd/gae-py-js

ADD requirements.txt /app/requirements.txt
RUN /env/bin/pip install -r requirements.txt

ADD . /app/
