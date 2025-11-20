# Dockerfile
FROM python:3.11-slim

# system deps for faiss, psycopg2 and build tools
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential \
      git \
      curl \
      libpq-dev \
      gcc \
      && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy only requirements first for caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy the app
COPY . /app

# create directory for FAISS index and make it writable
RUN mkdir -p /app/index_data
VOLUME ["/app/index_data"]

ENV PYTHONUNBUFFERED=1

# default command is to run uvicorn; docker-compose will override for worker
CMD ["uvicorn", "triage_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
