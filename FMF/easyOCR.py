import cv2
import os
import easyocr

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def crop_bib_region(img):
    h, w = img.shape[:2]
    # Adjust these ratios until the bib is fully inside the crop
    top = int(h * 0.45)
    bottom = int(h * 0.65)
    left = int(w * 0.35)
    right = int(w * 0.65)
    return img[top:bottom, left:right]

def extract_bib_numbers(image_path,filename):
    img = cv2.imread(image_path)
    if img is None:
        return []

    roi = crop_bib_region(img)

    # Save cropped ROI for visual confirmation
    # cv2.imwrite(r"C:\Work\FMF\Images\bib_crop_debug.jpg", roi)

    cv2.imwrite(os.path.join(r"C:\Work\Temp\\", filename), roi)

    results = reader.readtext(roi)
    bibs = []
    for (_, text, conf) in results:
        text = text.strip()
        if text.isdigit():
            bibs.append(text)
    return bibs

def process_folder(folder_path):
    tags = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)
            bibs = extract_bib_numbers(image_path,filename)
            tags[image_path] = bibs
            print(f"{filename}: {bibs}")
    return tags

if __name__ == "__main__":
    folder = r"C:\Work\FMF\Images"
    process_folder(folder)

# if __name__ == "__main__":
#     image_path = r"C:\Work\FMF\Images\SKB_6995.jpg"
#     bibs = extract_bib_numbers(image_path)
#     print("Detected bib numbers:", bibs)