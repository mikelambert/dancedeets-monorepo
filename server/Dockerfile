FROM gcr.io/dancedeets-hrd/gae-modules-py

ADD . /app/

CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
