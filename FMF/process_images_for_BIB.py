#====================================================================================
# Author: Sara 
# Created on: 8 Dec 2025
# Brief: Thispiece of code will read through all images and fidn teh BIB numbers and tag them accordingly.
#====================================================================================
#
import os
import cv2
import pytesseract
from collections import defaultdict

# Configure Tesseract path if needed (Windows users may need to specify)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Explicitly set path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_bib_numbers_from_image(image_path):
    """
    Extract bib numbers from a given image using OCR.
    Returns a list of detected numbers.
    """
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Optional: thresholding to improve OCR
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # OCR
    text = pytesseract.image_to_string(thresh, config="--psm 6 digits")

    # Extract only numbers (bib numbers are usually numeric)
    bib_numbers = [num for num in text.split() if num.isdigit()]

    return bib_numbers

def tag_images_in_folder(folder_path):
    """
    Reads all JPEG images in a folder and tags them with bib numbers.
    Returns a dictionary mapping image_path -> list of bib numbers.
    """
    image_tags = defaultdict(list)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".jpg"):
            image_path = os.path.join(folder_path, filename)
            bib_numbers = extract_bib_numbers_from_image(image_path)
            print (' Bib found : ', bib_numbers)
            image_tags[image_path] = bib_numbers
    return image_tags

# Example usage
imagefolder = r"C:\Work\FMF\Images"
image_tags = tag_images_in_folder(imagefolder)

# Print results
# for img, tags in image_tags.items():
#     print(f"{img}: {tags}")
