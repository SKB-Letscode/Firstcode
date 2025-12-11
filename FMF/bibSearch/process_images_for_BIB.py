#====================================================================================
# Author: Sara 
# Created on: 8 Dec 2025
# Brief: Thispiece of code will read through all images and fidn teh BIB numbers and tag them accordingly.
#====================================================================================
#
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_bib_numbers_from_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return []

    h, w = img.shape[:2]

    # Adjust these values to tightly crop the bib area
    top = int(h * 0.45)
    bottom = int(h * 0.65)
    left = int(w * 0.35)
    right = int(w * 0.65)

    roi = img[top:bottom, left:right]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = "--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(thresh, config=config)

    bib = "".join(ch for ch in text if ch.isdigit())

    return [bib] if bib else []



# image_path = r"C:\Work\FMF\Images\SKB_6995.jpg"

image_path = r"C:\Work\FMF\Images\SKB_7076.jpg"

bib_numbers = extract_bib_numbers_from_image(image_path)
print("Detected bib numbers:", bib_numbers)


