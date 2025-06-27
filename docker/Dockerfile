# AI Auto Tunneler Enhanced - Docker Image
FROM python:3.12-slim

LABEL maintainer="AI Auto Tunneler Team"
LABEL description="AI Auto Tunneler Enhanced - Termux Free Internet with AI Detection"
LABEL version="1.1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    stunnel4 \
    curl \
    wget \
    nmap \
    netcat-traditional \
    dnsutils \
    iputils-ping \
    net-tools \
    procps \
    jq \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/assets /app/core /etc/stunnel

# Generate SSL certificates for stunnel
RUN openssl req -new -x509 -days 365 -nodes \
    -out /etc/stunnel/cert.pem \
    -keyout /etc/stunnel/key.pem \
    -subj "/C=ID/ST=Jakarta/L=Jakarta/O=AI-Auto-Tunneler/CN=localhost"

# Make scripts executable
RUN chmod +x autorun.sh core/inject_engine.sh

# Create non-root user for security
RUN useradd -m -u 1000 tunneler && \
    chown -R tunneler:tunneler /app

# Switch to non-root user
USER tunneler

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python3", "main.py"]
