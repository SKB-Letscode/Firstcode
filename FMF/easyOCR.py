import cv2
import easyocr
import os

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

def extract_bib_easyocr(image_path):
    img = cv2.imread(image_path)
    crop, boxes = smart_bib_crop(img)
    if crop is None:
        return [], None

    # Second pass: read only the crop
    results = reader.readtext(crop)
    digits = [t.strip() for (_, t, c) in results if t.strip().isdigit()]

    # # Heuristic: choose the longest numeric string (most likely bib)
    # bib = max(digits, key=len) if digits else ""
    # return ([bib] if bib else []), crop
    return digits, crop

def process_folder(folder_path):
    tags = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)
            bibs, crop = extract_bib_easyocr(image_path)
            tags[image_path] = bibs
            print(f"{filename}: {bibs}")
    return tags

if __name__ == "__main__":
    folder = r"C:\Work\FMF\Images"
    process_folder(folder)


