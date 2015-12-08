# Dockerfile extending the generic Python image with application files for a
# single application.
FROM gcr.io/google_appengine/python-compat

ADD requirements.txt /app/
RUN pip install -r requirements.txt

ADD . /app
