# Adds application Python dependencies
FROM gcr.io/dancedeets-hrd/gae-modules

# Install application dependencies
COPY requirements.txt /tmp/requirements-app.txt
RUN pip install -r /tmp/requirements-app.txt

WORKDIR /app
