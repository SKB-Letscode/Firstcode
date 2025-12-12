#====================================================================================
# Author: Sara 
# Created on: 10 Dec 2025
# Brief: This script uses EasyOCR to detect and extract bib numbers from images adn updates to the local SQLite database TM_Images table.
# Precheck: 
#   1 - Make sure you have scalle down the image for faster processing
#   2 - Update the  MIN_LENGTH_OF_BIB_NUMBER value if needed 
#====================================================================================

import cv2
import easyocr
import os
import pandas as pd
import sqlite3
import sys

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.dbconnector import local_db_path

# Data configuration may get changed later
EventID = 1

# Added min size of bib number to fix the wrong behaviour of detecting "" as 66
MIN_LENGTH_OF_BIB_NUMBER = 3

reader = easyocr.Reader(['en'])
 
def smart_bib_crop(img, min_conf=0.4, expand=0.25):
    h, w = img.shape[:2]
    # results = reader.readtext(img)  # [(bbox, text, conf), ...]
    # Filter it to numeric while reading itself.
    results = reader.readtext(img, allowlist='0123456789') # [(bbox, text, conf), ...]

    # Collect numeric detections
    numeric_boxes = []
    for (bbox, text, conf) in results:
        if conf >= min_conf and text.strip().isdigit() and len(text.strip()) >= MIN_LENGTH_OF_BIB_NUMBER:
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
# Do pre processiong to improve OCR accuracy 
def preprocess_for_easyocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    th = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    opened = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    return opened


def extract_bib_easyocr(image_path):
    img = cv2.imread(image_path)
    # Not working properly need more analysis
    # cleanedimg = preprocess_for_easyocr(img)

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

def process_folder(folder_path,output_excel="bib_results.xlsx"):
    tags = {}
    results_list = []
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)

            bibs, img = extract_bib_easyocr(image_path)
                        
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
    # folder = r"C:\Work\FMF\Images\Downloads\Batch1"
    # process_folder(folder)
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT ID, TM_Images.FileName, TM_Images.FilePath
                    FROM TM_Images WHERE EventID = ?
                """, (EventID,))
    img_records = cursor.fetchall()    

    # Loop through all records and process each image
    processed_count = 0

    for img_info in img_records:
        img_id = img_info[0]
        img_filename = img_info[1]
        img_filepath = img_info[2]
        
        print(f"Processing {img_filename}...")
        
        # Extract bibs from the image
        bibs, img = extract_bib_easyocr(img_filepath) 
        bibs_str = ', '.join(bibs) if bibs else ''
        
        # Update the database with detected bibs
        cursor.execute("""
            UPDATE TM_Images 
            SET BibTags = ? 
            WHERE ID = ?
        """, (bibs_str, img_id))
        
        processed_count += 1
        print(f"  Found bibs: {bibs_str if bibs_str else 'None'}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"\n✅ Processed {processed_count} images and updated database")