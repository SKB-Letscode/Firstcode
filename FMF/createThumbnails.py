import os
import cv2

def create_thumbnails(input_folder, output_folder, size=(320, 240)):
    """
    Create thumbnails for all images in a folder.
    
    Args:
        input_folder (str): Path to the folder with original images.
        output_folder (str): Path to save thumbnails.
        size (tuple): Desired thumbnail size (width, height).
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path)

            if img is None:
                print(f"Skipping {filename} (could not read)")
                continue

            # Resize to thumbnail size
            # thumbnail = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
            thumbnail = cv2.resize(img, (1024, int(img.shape[0] * 1024 / img.shape[1])), interpolation=cv2.INTER_AREA)

            # Save thumbnail
            out_path = os.path.join(output_folder, filename)
            cv2.imwrite(out_path, thumbnail)

            print(f"Thumbnail saved: {out_path}")

if __name__ == "__main__":
    input_folder = r"C:\Work\FMF\Images"
    output_folder = r"C:\Work\FMF\Images\Thumbnails"
    create_thumbnails(input_folder, output_folder, size=(240,320))
