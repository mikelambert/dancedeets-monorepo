# DanceDeets Base Image
# Contains all system dependencies and Python packages
# This image is built infrequently and cached to speed up dev deploys

FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NODE_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    curl \
    git \
    ca-certificates \
    # For nginx
    nginx \
    # For memcached (pylibmc)
    libmemcached-dev \
    libsasl2-dev \
    # For GEOS/Shapely
    libgeos-dev \
    # For Pillow
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    # For image processing
    imagemagick \
    gifsicle \
    # For lxml/xml processing
    libxml2-dev \
    libxslt1-dev \
    # Misc
    netbase \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements-base.txt /tmp/requirements-base.txt
COPY requirements-app.txt /tmp/requirements-app.txt

# Install Python packages
RUN pip install --upgrade pip setuptools wheel \
    && pip install gunicorn gevent \
    && pip install -r /tmp/requirements-base.txt \
    && pip install -r /tmp/requirements-app.txt

# Configure nginx (ensure it can write to required directories)
RUN mkdir -p /var/lib/nginx/body /var/lib/nginx/proxy /var/lib/nginx/fastcgi /run \
    && chown -R www-data:www-data /var/lib/nginx
