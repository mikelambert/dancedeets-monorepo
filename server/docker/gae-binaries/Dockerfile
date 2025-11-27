# Adds image processing binaries (imagemagick, gifsicle)
FROM gcr.io/dancedeets-hrd/gae-geos

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        imagemagick \
        gifsicle \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
