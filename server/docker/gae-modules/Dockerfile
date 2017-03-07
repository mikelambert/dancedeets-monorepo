FROM gcr.io/dancedeets-hrd/gae-geos

ADD install_re2.sh /app/install_re2.sh
RUN /bin/bash /app/install_re2.sh

ADD requirements.txt /app/requirements.txt
RUN /env/bin/pip install -r /app/requirements.txt

