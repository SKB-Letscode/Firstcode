#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: This script basically a Utility bundled with all imaeg related tools.
#====================================================================================
import numpy as np
import os
import boto3
import cv2

from PIL import Image

# Small funtion to resize image during face identification process for fast performance
def resize_image(img_path, max_dim):
    # Open image, scale down preserving aspect ratio and return RGB numpy array
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image file not found at: {img_path}")
    
    try:
        with Image.open(img_path) as img:
            img = img.convert('RGB')
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)
            return np.array(img)
    except Exception as e:
        print(f"Error resizing image {img_path}: {e}")
        raise Exception(f"Failed to open/resize image: {str(e)}")   

# Methods to deal with AWS S3 bucket

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

def create_thumbnails(input_folder, output_folder, size=(320, 240)):
    """
    Create thumbnails for all images in a folder.
    
    Args:
        input_folder (str): Path to the folder with original images.
        output_folder (str): Path to save thumbnails.
        size (tuple): Desired thumbnail size (width, height).
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path)

            if img is None:
                print(f"Skipping {filename} (could not read)")
                continue

            # Resize to thumbnail size
            # thumbnail = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
            # thumbnail = cv2.resize(img, (1024, int(img.shape[0] * 1024 / img.shape[1])), interpolation=cv2.INTER_AREA)
            thumbnail = cv2.resize(img, (320, int(img.shape[0] * 320 / img.shape[1])), interpolation=cv2.INTER_AREA)

            # Save thumbnail
            out_path = os.path.join(output_folder, filename)
            cv2.imwrite(out_path, thumbnail)

            print(f"Thumbnail saved: {out_path}")