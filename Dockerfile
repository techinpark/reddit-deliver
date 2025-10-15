# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY setup.py .

# Install the package
RUN pip install --no-cache-dir -e .

# Create directories for data and config
RUN mkdir -p /app/data /app/config

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set volumes for persistent data
VOLUME ["/app/data", "/app/config"]

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command - start monitor in daemon mode
CMD ["reddit-deliver", "monitor", "start", "--daemon"]
