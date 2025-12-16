
#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: This script is to expose apis for uplaod / search images 
#           by end users can be used by any other cluient apps/pages.
# uvicorn app.face_search_api:app --reload
#====================================================================================
#
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sqlite3
import faiss
import pickle
import numpy as np
import face_recognition

from app.imgTools.imgTools import resize_image
from PIL import Image
from app.dbconnector import local_db_path, local_index_path, local_meta_path, LOCAL_IMAGE_FOLDER

# Used for resizing images
MAX_DIM = 800

# Distance threshold: only return matches with distance <= this value
DISTANCE_THRESHOLD = 0.19

index = faiss.read_index(local_index_path)
with open(local_meta_path, 'rb') as f:
    face_ids = pickle.load(f)

app = FastAPI(title="Face Search API")

# Enable CORS for web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images
thumbnails_path = os.path.join(LOCAL_IMAGE_FOLDER, "Downloads", "Thumbnails")
if os.path.exists(thumbnails_path):
    app.mount("/images", StaticFiles(directory=thumbnails_path), name="images")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/search-face")
async def search_face(file: UploadFile = File(...), top_k: int = 5):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    # Resize before encoding to reduce memory and speed up processing
    try:
        img = resize_image(temp_path, MAX_DIM)
    except Exception:
        # fallback to loading original if resize fails
        img = face_recognition.load_image_file(temp_path)

    uploaded_faces = face_recognition.face_encodings(img)
    os.remove(temp_path)
    results = []

    for face_emb in uploaded_faces:
        face_emb = np.expand_dims(face_emb.astype('float32'), axis=0)
        distances, indices = index.search(face_emb, top_k)
        for j, i in enumerate(indices[0]):
            dist = float(distances[0][j])
            # only include matches at or below the threshold
            if dist <= DISTANCE_THRESHOLD:
                matched_face_id = face_ids[i]
                conn = sqlite3.connect(local_db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TM_Images.FileName, TM_Images.FilePath
                    FROM TM_Faces
                    JOIN TM_Images ON TM_Faces.ImageID = TM_Images.ID
                    WHERE TM_Faces.FaceID = ?
                """, (matched_face_id,))
                img_info = cursor.fetchone()
                conn.close()
                if img_info:
                    # Return thumbnail filename for web serving
                    thumbnail_name = os.path.basename(img_info[1])
                    results.append({"FileName": img_info[0], "ThumbnailUrl": f"/images/{thumbnail_name}", "FilePath": img_info[1], "Distance": float(distances[0][j])})
                else:
                    results.append("No Matching Image Found")
    return {"matches": results}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
