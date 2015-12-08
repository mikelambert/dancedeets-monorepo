# Dockerfile extending the generic Python image with application files for a
# single application.
FROM gcr.io/google_appengine/python-compat

RUN pip install google-python-cloud-debugger

ADD requirements.txt /app/
RUN pip install -r requirements.txt

ADD . /app
