# Adds core Python dependencies (memcached, Google Cloud clients)
FROM gcr.io/dancedeets-hrd/gae-binaries

# Install memcached libs and lxml dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libmemcached-dev \
        libsasl2-dev \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install core Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install gunicorn gevent \
    && pip install -r /tmp/requirements.txt
