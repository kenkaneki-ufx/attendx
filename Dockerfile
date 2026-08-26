# AttendX Dockerfile for Koyeb Deployment
# Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies for PostgreSQL and image processing
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Koyeb will use $PORT)
EXPOSE 8000

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Default superuser credentials (can be overridden via env vars)
ENV SUPERUSER_USERNAME=admin
ENV SUPERUSER_EMAIL=admin@attendx.com
ENV SUPERUSER_PASSWORD=admin123

# Start command
CMD ["./start.sh"]