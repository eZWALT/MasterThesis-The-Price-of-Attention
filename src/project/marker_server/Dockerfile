FROM python:3.11-slim

WORKDIR /app

# Install runtime deps (optional pylsl/psychopy — failure is non-fatal)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true

COPY . .

EXPOSE 9876

ENV MARKER_HOST=0.0.0.0
ENV MARKER_PORT=9876
ENV MARKER_BACKEND=log
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "server.py"]
