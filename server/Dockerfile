FROM gcr.io/dancedeets-hrd/gae-modules-py

ADD . /app/

# Make entrypoint executable (in case git didn't preserve permissions)
RUN chmod +x /app/entrypoint.sh

# Use entrypoint script that starts both Node.js render server and gunicorn
CMD ["/app/entrypoint.sh"]
