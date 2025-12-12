#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: This Windows UI Application is an Utility to upload images to S3 bucket.
#====================================================================================
#
import tkinter as tk
from tkinter import filedialog, messagebox
import boto3
import os

# S3 bucket name which si configured in aws CLI
bucket_name = "sara-s3-bucket"
# S3 subfolder path
subfolder = "FMF/FMFImages"

def upload_folder_to_s3(folder_path):
    s3 = boto3.client('s3')
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                # Add subfolder to the key
                key = f"{subfolder}/{os.path.basename(file_path)}"
                s3.upload_file(file_path, bucket_name, key)
    messagebox.showinfo("Upload Complete", f"All images uploaded to {bucket_name}")

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        upload_folder_to_s3(folder_path)

root = tk.Tk()
root.title("Find My Face : Upload Images to Cloud...")
tk.Button(root, text="Select Folder and Upload", command=select_folder).pack(pady=20)
root.mainloop()