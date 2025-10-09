FROM python:3.11-slim

LABEL maintainer="Sunday Natural Products GmbH"
ARG UID=1000
ARG GID=1000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -g $GID metrics && \
    useradd -u $UID -g $GID -m -s /bin/bash metrics

# Copy requirements
COPY ./metrics-dashboard/requirements.txt /tmp/requirements.txt

# Install Python packages
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp/*

# Create directories with proper permissions (BEFORE switching user!)
RUN mkdir -p /app/templates /app/static/css /app/static/js /app/utils /app/data/history && \
    chmod -R 777 /app/data && \
    chown -R metrics:metrics /app

# Copy application files
COPY --chown=metrics:metrics ./metrics-dashboard/*.py /app/
COPY --chown=metrics:metrics ./metrics-dashboard/templates/ /app/templates/
COPY --chown=metrics:metrics ./metrics-dashboard/static/ /app/static/
COPY --chown=metrics:metrics ./metrics-dashboard/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV METRICS_DATA_DIR=/app/data
ENV ROBOT_RESULTS_DIR=/robot_results

WORKDIR /app
USER metrics
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]