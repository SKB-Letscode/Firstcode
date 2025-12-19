#!/usr/bin/env bash
# Render build script with memory optimization

set -e

echo "=== Upgrading pip ==="
pip install --upgrade pip setuptools wheel

echo "=== Installing lightweight dependencies first ==="
pip install --no-cache-dir fastapi uvicorn[standard] requests

echo "=== Installing numpy and Pillow ==="
pip install --no-cache-dir numpy==1.26.4 Pillow==10.4.0

echo "=== Installing cmake for dlib ==="
pip install --no-cache-dir cmake

echo "=== Installing dlib (this may take a few minutes) ==="
pip install --no-cache-dir dlib==19.24.6

echo "=== Installing face recognition ==="
pip install --no-cache-dir face_recognition_models==0.3.0
pip install --no-cache-dir face_recognition==1.3.0

echo "=== Installing FAISS (lighter version) ==="
pip install --no-cache-dir faiss-cpu==1.8.0

echo "=== Installing boto3 ==="
pip install --no-cache-dir boto3==1.35.0

echo "=== Creating necessary directories ==="
mkdir -p DB Images/Downloads/Batch1/Thumbnails

echo "=== Build completed successfully ==="
