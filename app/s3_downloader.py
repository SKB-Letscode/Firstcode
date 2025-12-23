"""
S3 File Downloader for Render Deployment
Downloads DB and Image files from S3 on startup
"""
import os
import boto3
from botocore.exceptions import ClientError

def download_from_s3():
    """Download necessary files from S3 bucket"""
    
    # S3 Configuration
    bucket_name = os.getenv('S3_BUCKET_NAME', 'sara-s3-bucket')
    aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    # Local paths
    db_folder = os.getenv('DB_FOLDER', '/opt/render/project/src/DB')
    image_folder = os.getenv('IMAGE_FOLDER', '/opt/render/project/src/Images')
    
    # Create folders if they don't exist
    os.makedirs(db_folder, exist_ok=True)
    os.makedirs(image_folder, exist_ok=True)
    
    print("\n=== Starting S3 Download ===")
    print(f"Bucket: {bucket_name}")
    print(f"Region: {aws_region}")
    print(f"Local DB folder: {db_folder}")
    print(f"Local Image folder: {image_folder}")
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3', region_name=aws_region)
        
        # Files to download from S3
        db_files = [
            ('FMF/SQLiteDB/1_ImageDB.sqlite', '1_ImageDB.sqlite'),
            ('FMF/SQLiteDB/1_faiss_face_index.bin', '1_faiss_face_index.bin'),
            ('FMF/SQLiteDB/1_face_metadata.pkl', '1_face_metadata.pkl')
        ]
        
        # Download DB files
        print("\n--- Downloading DB files ---")
        for s3_key, local_filename in db_files:
            local_path = os.path.join(db_folder, local_filename)
            
            # Skip if file already exists
            if os.path.exists(local_path):
                print(f"✓ {local_filename} already exists (size: {os.path.getsize(local_path)} bytes)")
                continue
            
            try:
                print(f"Downloading {s3_key}...")
                s3_client.download_file(bucket_name, s3_key, local_path)
                file_size = os.path.getsize(local_path)
                print(f"✓ Downloaded {local_filename} ({file_size} bytes)")
            except ClientError as e:
                print(f"✗ Failed to download {s3_key}: {e}")
                return False
        
        # Download Images folder
        print("\n--- Downloading Images ---")
        try:
            # List all objects in the Images folder
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix='FMF/FMFImages/')
            
            image_count = 0
            for page in pages:
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    s3_key = obj['Key']
                    
                    # Skip if it's just the folder prefix
                    if s3_key.endswith('/'):
                        continue
                    
                    # Get relative path (remove prefix)
                    relative_path = s3_key.replace('FMF/FMFImages/', '')
                    local_path = os.path.join(image_folder, relative_path)
                    
                    # Create subdirectories if needed
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    
                    # Skip if file already exists
                    if os.path.exists(local_path):
                        continue
                    
                    # Download file
                    s3_client.download_file(bucket_name, s3_key, local_path)
                    image_count += 1
                    
                    if image_count % 10 == 0:
                        print(f"Downloaded {image_count} images...")
            
            print(f"✓ Downloaded {image_count} images total")
            
        except ClientError as e:
            print(f"✗ Failed to download images: {e}")
            return False
        
        print("\n=== S3 Download Complete ===\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during S3 download: {e}")
        print("Make sure AWS credentials are set correctly in Render environment variables:")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - AWS_DEFAULT_REGION")
        print("  - S3_BUCKET_NAME")
        return False

if __name__ == "__main__":
    download_from_s3()
