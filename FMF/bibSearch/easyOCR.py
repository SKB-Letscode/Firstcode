
#====================================================================================
# Author: Sara 
# Created on: 10 Dec 2025
# Brief: This script uses EasyOCR to detect and extract bib numbers from images.
# uvicorn app.face_search_api:app --reload
#====================================================================================
#
import cv2
import easyocr
import os
import pandas as pd

reader = easyocr.Reader(['en'])

def smart_bib_crop(img, min_conf=0.4, expand=0.25):
    h, w = img.shape[:2]
    results = reader.readtext(img)  # [(bbox, text, conf), ...]

    # Collect numeric detections
    numeric_boxes = []
    for (bbox, text, conf) in results:
        if conf >= min_conf and text.strip().isdigit():
            # bbox is 4 points: [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            x1, y1 = int(min(xs)), int(min(ys))
            x2, y2 = int(max(xs)), int(max(ys))
            numeric_boxes.append((x1, y1, x2, y2, text, conf))

    if not numeric_boxes:
        return None, []  # No numeric text found

    # Merge overlapping boxes into a single bib region
    x1 = min(b[0] for b in numeric_boxes)
    y1 = min(b[1] for b in numeric_boxes)
    x2 = max(b[2] for b in numeric_boxes)
    y2 = max(b[3] for b in numeric_boxes)

    # Expand the box to include surrounding bib area
    bw, bh = x2 - x1, y2 - y1
    x1 = max(0, int(x1 - expand * bw))
    y1 = max(0, int(y1 - expand * bh))
    x2 = min(w, int(x2 + expand * bw))
    y2 = min(h, int(y2 + expand * bh))

    crop = img[y1:y2, x1:x2]
    return crop, numeric_boxes
# Version 1 - Gives unnecessary 66 and also misses when multiple bibs 
def extract_bib_easyocr(image_path):
    img = cv2.imread(image_path)
    crop, boxes = smart_bib_crop(img)
    if crop is None:
        return [], None

    # Second pass: read only the crop
    results = reader.readtext(crop)
    digits = [t.strip() for (_, t, c) in results if t.strip().isdigit() and c >= 0.5]

    # # Heuristic: choose the longest numeric string (most likely bib)
    # bib = max(digits, key=len) if digits else ""
    # return ([bib] if bib else []), crop
    return digits, crop

# # Version 2 - to fix Version 1 issues
# Key improvements:

# Higher confidence threshold (0.5 → 0.6): Reduces false positives like random "66"
# Minimum bib length filter (≥2 or ≥3 digits): Prevents single digits from being detected
# Duplicate removal: Uses a seen set to avoid detecting the same number twice
# Process full image: Removed the crop step which might have been missing some bibs
# Two-pass detection: First tries strict thresholds, then relaxes if nothing found
# Sort by length: Longer numbers appear first (typically more reliable bibs)
def extract_bib_easyocrV2(image_path, min_conf=0.5, min_bib_length=2):
    """
    Extract bib numbers from an image.
    
    Args:
        image_path: Path to the image file
        min_conf: Minimum confidence threshold (0.5 is more strict)
        min_bib_length: Minimum number of digits for a valid bib (filters out single digits)
    """
    img = cv2.imread(image_path)

    # img = cv2.imread(image_path)
    # crop, boxes = smart_bib_crop(img)

    if img is None:
        return [], None
    
    # Read text from full image (not just cropped region)
    results = reader.readtext(img)
    
    # Filter numeric text with stricter criteria
    bibs = []
    seen = set()  # To avoid duplicates
    
    for (bbox, text, conf) in results:
        cleaned = text.strip()
        
        # More strict filtering:
        # 1. Must be numeric
        # 2. Must meet minimum confidence
        # 3. Must meet minimum length (filters out single digits like "6")
        # 4. Not already seen (avoid duplicates)
        if (cleaned.isdigit() and 
            conf >= min_conf and 
            len(cleaned) >= min_bib_length and 
            cleaned not in seen):
            bibs.append(cleaned)
            seen.add(cleaned)
    
    # Sort by length descending (longer numbers are more likely real bibs)
    bibs.sort(key=len, reverse=True)
    
    return bibs, img


def process_folder(folder_path,output_excel="bib_results.xlsx"):
    tags = {}
    results_list = []
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)

            # Call Version 1
            bibs, img = extract_bib_easyocr(image_path)

            # Call Version 2
            # # Try with higher confidence threshold first
            # bibs, img = extract_bib_easyocrV2(image_path, min_conf=0.6, min_bib_length=3)
            
            # # If no results, try with relaxed thresholds
            # if not bibs:
            #     bibs, img = extract_bib_easyocrV2(image_path, min_conf=0.4, min_bib_length=2)
                        
            tags[image_path] = bibs
            print(f"{filename}: {bibs}")
            
            # Add to results list
            results_list.append({
                'Filename': filename,
                'Path': image_path,
                'Bibs': ', '.join(bibs) if bibs else ''
            })    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(results_list)
    df.to_excel(output_excel, index=False)
    print(f"\n✅ Results saved to {output_excel}")

    return tags

if __name__ == "__main__":
    # folder = r"C:\Work\FMF\Images"
    folder = r"C:\Work\FMF\Images\Downloads\Batch1"
    process_folder(folder)