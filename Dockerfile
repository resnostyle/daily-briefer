FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PYTHONPATH=/app

# Default: run all briefs. Override with one script name to run that script only, e.g.:
#   docker run ... github  |  docker run ... post quote
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
