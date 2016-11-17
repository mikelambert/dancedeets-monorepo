FROM gcr.io/dancedeets-hrd/gae-py-js

ADD install_re2.sh /app/install_re2.sh
RUN /bin/bash install_re2.sh

ADD requirements.txt /app/requirements.txt
RUN /env/bin/pip install -r requirements.txt

ADD . /app/
