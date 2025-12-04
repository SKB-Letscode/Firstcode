#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: This script basically a Utility to deal with s3 bucket to upload / download files.
# git hub test checking fixing personal user id for commit - SKB
#====================================================================================

import os
import boto3

s3 = boto3.client('s3')
# plain bucket name (no "s3://" prefix)
bucket_name = "sara-s3-bucket"

def download_from_s3(s3_key, local_path):
    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
    try:
        s3.download_file(bucket_name, s3_key, local_path)
    except Exception as e:
        print(f"Error downloading {s3_key} from S3: {e}")
        raise

def upload_to_s3(local_path, s3_key):
    try:
        s3.upload_file(local_path, bucket_name, s3_key)
    except Exception as e:
        print(f"Error uploading {local_path} to s3://{bucket_name}/{s3_key}: {e}")
        raise