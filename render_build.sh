#!/usr/bin/env bash
# Render build script

set -e

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Creating necessary directories ==="
mkdir -p DB Images/Downloads/Batch1/Thumbnails

echo "=== Build completed successfully ==="
