FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN mkdir -p /app/index_data
VOLUME ["/app/index_data"]

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.triage_api:app", "--host", "0.0.0.0", "--port", "8000"]
