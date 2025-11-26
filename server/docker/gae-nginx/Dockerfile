# Adds nginx to the base image
FROM gcr.io/dancedeets-hrd/gae-py-js

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/lib/nginx/body /var/lib/nginx/proxy /var/lib/nginx/fastcgi /run \
    && chown -R www-data:www-data /var/lib/nginx
