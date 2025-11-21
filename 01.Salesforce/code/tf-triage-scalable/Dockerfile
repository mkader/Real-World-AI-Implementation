FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all code
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Ensure Python can import the "api" package
ENV PYTHONPATH=/app

# Default command (overridden by docker-compose)
CMD ["python", "api/build_index.py"]
