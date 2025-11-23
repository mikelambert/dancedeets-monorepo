# DanceDeets App Engine Flexible Environment Dockerfile
# Multi-stage build for Python + Node.js + Nginx

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

# Install Python dependencies first (for caching)
COPY docker/gae-modules/requirements.txt /tmp/requirements-base.txt
COPY docker/gae-modules-py/requirements.txt /tmp/requirements-app.txt

# Create a combined requirements file and install
RUN pip install --upgrade pip setuptools wheel \
    && pip install gunicorn gevent \
    && pip install -r /tmp/requirements-base.txt || true \
    && pip install -r /tmp/requirements-app.txt || true

# Install Node.js dependencies for the render server
COPY package.json package-lock.json* /app/
RUN npm install --omit=dev || true

# Copy application code
COPY . /app/

# Configure nginx (ensure it can write to required directories)
RUN mkdir -p /var/lib/nginx/body /var/lib/nginx/proxy /var/lib/nginx/fastcgi /run \
    && chown -R www-data:www-data /var/lib/nginx

# Make startup script executable
RUN chmod +x /app/run-servers.sh

# Expose the port that App Engine expects
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/_ah/health || exit 1

# Run the startup script
ENTRYPOINT ["bash", "/app/run-servers.sh"]
