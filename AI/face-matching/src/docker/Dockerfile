FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for OpenCV and face recognition
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libatspi2.0-0 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install core packages first
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU version (lighter for Docker)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy application code
COPY . .

# Create directories for model cache and logs
RUN mkdir -p ./models ./logs ./temp

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "1", "-b", "0.0.0.0:8001", "--timeout", "120", "backend.api.main:app"]
