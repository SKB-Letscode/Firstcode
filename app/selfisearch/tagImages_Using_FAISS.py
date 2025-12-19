#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: Detect faces in images, store embeddings in SQLite DB, and build FAISS index.
# Precondition :
#   1 - Create a folder and place all images to be processed in it
#   2 - Update LOCAL_IMAGE_FOLDER path to point to that folder
#====================================================================================
import os
import sys
import sqlite3
import numpy as np
import faiss
import pickle
import face_recognition

from PIL import Image

# Add the workspace root to Python path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from app.imgTools.imgTools import resize_image  

from app.dbconnector import LOCAL_IMAGE_FOLDER,local_db_path,local_index_path,local_meta_path,LOCAL_IMAGE_FOLDER

from app.dbconnector import init_db


# Data configuration may get changed later
EventID = 1

# Used for resizing images
MAX_DIM = 800

# # Local file names
# DB_FILE =  str(EventID) +"_ImageDB.sqlite"
# INDEX_FILE = str(EventID) +"_faiss_face_index.bin"
# META_FILE = str(EventID) +"_face_metadata.pkl"
# LOCAL_DB_FOLDER = r"C:\Work\FMF\DB"  # Local folder to store DB
# LOCAL_IMAGE_FOLDER = r"C:\Work\FMF\Images\Downloads\Batch1"

# # Full local paths

# local_db_path = os.path.join(LOCAL_DB_FOLDER, DB_FILE)
# local_index_path = os.path.join(LOCAL_DB_FOLDER, INDEX_FILE)
# local_meta_path = os.path.join(LOCAL_DB_FOLDER, META_FILE)


# function to store the images and face idendified in the image to a db tables   
def store_image_and_faces(file_name, file_path, face_embeddings):
    # Store image and its face embeddings in DB
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO TM_Images (EventID, FileName, FilePath) VALUES (?, ?, ?)", (EventID, file_name, file_path))
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