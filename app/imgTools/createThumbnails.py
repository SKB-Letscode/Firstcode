#====================================================================================
# Author: Sara 
# Created on: 10 Dec 2025
# Brief: This script will creates scale down thumbnails for images for fast processing.
#====================================================================================
#
import os
import sys
import cv2

# Add workspace root to path to find app module
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, workspace_root)

from app.imgTools.imgTools import create_thumbnails

# Main sub 
if __name__ == "__main__":
    input_folder = r"C:\Work\FMF\Images\Downloads"
    output_folder = r"C:\Work\FMF\Images\Downloads\Thumbnails"
    create_thumbnails(input_folder, output_folder, size=(320,240))
    print(f"Thumbnails created in: {output_folder}")

    

    