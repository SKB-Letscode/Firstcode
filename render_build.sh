#!/usr/bin/env bash
# Render build script for Starter plan

set -e

echo "=== Upgrading pip ==="
pip install --upgrade pip setuptools wheel

echo "=== Installing core dependencies ==="
pip install --no-cache-dir numpy==1.26.4
pip install --no-cache-dir Pillow==10.4.0
pip install --no-cache-dir fastapi==0.115.0
pip install --no-cache-dir "uvicorn[standard]==0.30.0"
pip install --no-cache-dir requests==2.32.3

echo "=== Installing dlib (may take 5-10 minutes) ==="
pip install --no-cache-dir cmake
pip install --no-cache-dir dlib==19.24.6

echo "=== Installing face recognition ==="
pip install --no-cache-dir face_recognition_models==0.3.0
pip install --no-cache-dir face_recognition==1.3.0

echo "=== Installing FAISS ==="
pip install --no-cache-dir faiss-cpu==1.8.0

echo "=== Installing boto3 ==="
pip install --no-cache-dir boto3==1.35.0

echo "=== Verifying installation ==="
python -c "import face_recognition; import faiss; import numpy; print('All packages imported successfully!')"

echo "=== Build completed successfully ==="
