# Adds GEOS library for Shapely geospatial support
FROM gcr.io/dancedeets-hrd/gae-nginx

# Install GEOS from Debian packages (much faster than compiling from source)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgeos-dev \
    && rm -rf /var/lib/apt/lists/*
