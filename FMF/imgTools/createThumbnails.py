#====================================================================================
# Author: Sara 
# Created on: 10 Dec 2025
# Brief: This script will creates scale down thumbnails for images for fast processing.
#====================================================================================
#
import os
import cv2
from app.imgTools.imgTools import create_thumbnails

# Main sub 
if __name__ == "__main__":
    input_folder = r"C:\Work\FMF\Images\Downloads"
    output_folder = r"C:\Work\FMF\Images\Downloads\Thumbnails"
    create_thumbnails(input_folder, output_folder, size=(320,240))

    