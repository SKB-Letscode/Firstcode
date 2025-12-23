FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages one by one to avoid memory spikes
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir numpy==1.26.4
RUN pip install --no-cache-dir Pillow==10.4.0
RUN pip install --no-cache-dir fastapi==0.115.0
RUN pip install --no-cache-dir "uvicorn[standard]==0.30.0"
RUN pip install --no-cache-dir requests==2.32.3

# Install dlib (memory intensive, done separately)
RUN pip install --no-cache-dir dlib==19.24.6

# Install face recognition
RUN pip install --no-cache-dir face_recognition_models==0.3.0
RUN pip install --no-cache-dir face_recognition==1.3.0

# Install remaining packages
RUN pip install --no-cache-dir faiss-cpu==1.9.0.post1
RUN pip install --no-cache-dir boto3==1.35.0

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start command
CMD ["uvicorn", "app.server.api_services:service", "--host", "0.0.0.0", "--port", "8000"]
