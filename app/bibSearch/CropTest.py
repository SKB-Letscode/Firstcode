import cv2

image_path = r"C:\Work\FMF\Images\SKB_6995.jpg"
output_path = r"C:\Work\FMF\Images\SKB_6995_crop.jpg"

img = cv2.imread(image_path)
h, w = img.shape[:2]

# Adjust crop coordinates until the bib is fully inside
# top = int(h * 0.45)
# bottom = int(h * 0.65)
# left = int(w * 0.35)
# right = int(w * 0.65)

image_path = r"C:\Work\FMF\Images\SKB_6995.jpg"
output_path = r"C:\Work\FMF\Images\SKB_6995_crop.jpg"

img = cv2.imread(image_path)
h, w = img.shape[:2]

# Adjust crop coordinates until the bib is fully inside
top = int(h * 0.35)
bottom = int(h * 0.55)
left = int(w * 0.35)
right = int(w * 0.65)

roi = img[top:bottom, left:right]

# Save cropped region
cv2.imwrite(output_path, roi)

print(f"Cropped bib image saved to: {output_path}")

roi = img[top:bottom, left:right]

# Save cropped region
cv2.imwrite(output_path, roi)

print(f"Cropped bib image saved to: {output_path}")
