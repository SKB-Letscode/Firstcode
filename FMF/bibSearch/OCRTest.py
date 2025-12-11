import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

image_path = r"C:\Work\FMF\Images\SKB_6995.jpg"

img = cv2.imread(image_path)

# Run OCR directly on the raw image
config = "--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789"
ocr_data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)

# Debug: print what Tesseract saw
for i in range(len(ocr_data["text"])):
    text = ocr_data["text"][i].strip()
    conf = ocr_data["conf"][i]
    if text:
        print(f"Token: {text}, Confidence: {conf}")
