FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

ENV PYTHONPATH=/app

# Default: run daily briefing so "docker run ..." does one full run
CMD ["python", "scripts/daily_briefing.py"]
