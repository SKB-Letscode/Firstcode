#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: Detect faces in images, store embeddings in SQLite DB, and build FAISS index.
# Github code checking Test with Personal ID
#====================================================================================

import os
import sqlite3
import numpy as np
import faiss
import pickle
import face_recognition

from PIL import Image
# Used for resizing images
MAX_DIM = 800

# AWS S3 Config
s3_bucket_name = "sara-s3-bucket"
s3_db_folder_prefix = r"FMF/SQLiteDB"  # S3 subfolder where DB is stored
s3_imagefolder_prefix = r"FMF/FMFImages/"  # S3 image folder folder path
local_db_folder = r"C:\Work\FMF\DB"  # Local folder to store DB


# Local file names
DB_FILE = "ImageDB.sqlite"
INDEX_FILE = "faiss_face_index.bin"
META_FILE = "face_metadata.pkl"

# Full local paths
local_db_path = os.path.join(local_db_folder, DB_FILE)
local_index_path = os.path.join(local_db_folder, INDEX_FILE)
local_meta_path = os.path.join(local_db_folder, META_FILE)

# Local sub folders 
LOCAL_IMAGE_FOLDER = r"C:\Work\FMF\Images"

# Initialize DB
def init_db():
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TM_Images (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName TEXT,
            FilePath TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TM_Faces (
            FaceID INTEGER PRIMARY KEY AUTOINCREMENT,
            ImageID INTEGER,
            Embedding BLOB,
            FOREIGN KEY(ImageID) REFERENCES TM_Images(ID)
        )
    """)
    conn.commit()
    conn.close()
# Small funtion to resize image during face identification process for fast performance
def resize_image(img_path, max_dim=MAX_DIM):
    # Open image, scale down preserving aspect ratio and return RGB numpy array
    img = Image.open(img_path).convert('RGB')
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    return np.array(img)
# function to store the images and face idendified in the image to a db tables   
def store_image_and_faces(file_name, file_path, face_embeddings):
    # Store image and its face embeddings in DB
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO TM_Images (FileName, FilePath) VALUES (?, ?)", (file_name, file_path))
    image_id = cursor.lastrowid
    for emb in face_embeddings:
        cursor.execute("INSERT INTO TM_Faces (ImageID, Embedding) VALUES (?, ?)", (image_id, pickle.dumps(emb)))
    conn.commit()
    conn.close()

# Main function which loops through the  image folder and process each image
def process_images(folder_path):
    # Detect faces and store embeddings. Images are resized before encoding
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(folder_path, file)
            try:
                img_small = resize_image(img_path, MAX_DIM)
            except Exception as e:
                print(f"Failed to open/resize {file}: {e}")
                continue
            # If multipe faces adentified in the image will return the list of face encodings
            face_encodings = face_recognition.face_encodings(img_small)
            if face_encodings:
                store_image_and_faces(file, img_path, face_encodings)
                print(f"Processed {file}: {len(face_encodings)} faces (resized to max {MAX_DIM}px)")

def build_faiss_index():
    # Build FAISS, Face book AI Simalirit Search index from face embeddings in DB for fast and quick access during search
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT FaceID, Embedding FROM TM_Faces")
    rows = cursor.fetchall()
    conn.close()

    face_ids = []
    embeddings = []

    for face_id, emb_blob in rows:
        face_ids.append(face_id)
        embeddings.append(pickle.loads(emb_blob))

    embeddings = np.array(embeddings).astype('float32')

    # Create FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save index and metadata
    faiss.write_index(index, local_index_path)
    with open(local_meta_path, 'wb') as f:
        pickle.dump(face_ids, f)

    print(f"FAISS index built with {len(face_ids)} faces.")

# Main method whihc inits db process images and build faiss index
if __name__ == "__main__":
    init_db()
    process_images(LOCAL_IMAGE_FOLDER)
    build_faiss_index()