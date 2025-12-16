
#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: This script is to expose apis for uplaod / search images 
#           by end users can be used by any other cluient apps/pages.
# uvicorn uvicorn app.server.api_services:service --reload
#====================================================================================
#
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import sqlite3
import faiss
import pickle
import numpy as np
import face_recognition

from app.imgTools.imgTools import resize_image
from PIL import Image
from app.dbconnector import local_db_path, local_index_path, local_meta_path

# Request model for BIB search
class BibSearchRequest(BaseModel):
    bib_number: str

# Base image location for thumbnails
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
THUMBNAILS_FOLDER = os.path.join(workspace_root, "Images", "Downloads", "Thumbnails")

# Used for resizing images
MAX_DIM = 800

# Distance threshold: only return matches with distance <= this value
DISTANCE_THRESHOLD = 0.19

index = faiss.read_index(local_index_path)
with open(local_meta_path, 'rb') as f:
    face_ids = pickle.load(f)

# -----------------------------------------------------------------------------------------------------
# Service to get list of faces matching the uploaded image
# Receives the face image file and top_k number of matches to return
# -----------------------------------------------------------------------------------------------------

service = FastAPI(title="Face Search API")

# Enable CORS for web application
service.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Web directory (under app folder)
# Get app folder (1 level up from api_services.py: server -> app)
app_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
web_folder = os.path.join(app_folder, "web")
if os.path.exists(web_folder):
    service.mount("/web", StaticFiles(directory=web_folder), name="web")

@service.get("/")
def read_root():
    """Serve the web application"""
    # Look for index.html in app/web folder
    app_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    web_folder = os.path.join(app_folder, "web")
    index_path = os.path.join(web_folder, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Web app not found. Looking for: {index_path}"}

@service.get("/health")
def health_check():
    return {"status": "ok"}

@service.get("/images/{filename}")
def get_image(filename: str):
    """Serve thumbnail images from the Images/Downloads/Thumbnails folder"""
    image_path = os.path.join(THUMBNAILS_FOLDER, filename)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found", "path": image_path}

@service.get("/logo")
def get_logo():
    """Serve the logo image"""
    logo_path = os.path.join(workspace_root, "Images", "support", "flashbulbzz.jpg")
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    return {"error": "Logo not found", "path": logo_path}

@service.post("/search-face")
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
                    # Extract thumbnail filename from FilePath
                    thumbnail_name = os.path.basename(img_info[1])
                    results.append({
                        "FileName": img_info[0], 
                        "FilePath": img_info[1], 
                        "ThumbnailUrl": f"/images/{thumbnail_name}",
                        "Distance": float(distances[0][j])
                    })
                else:
                    results.append("No Matching Image Found")
    return {"matches": results}

# -----------------------------------------------------------------------------------------------------
# Service to get list of images matching the BIB number
# Receives the bib number to search for and does like search as one image may have multiple bibs tagged
# -----------------------------------------------------------------------------------------------------

@service.post("/search-bib")
async def search_bib(request: BibSearchRequest):
    """
    Search for images by BIB number.
    
    Args:
        request: BibSearchRequest containing the bib_number to search for
    
    Returns:
        JSON with list of matching images (ID, FileName, FilePath)
    """
    bib_number = request.bib_number
    results = []
    
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    
    # Search for exact match or comma-separated bibs containing this number
    cursor.execute("""
        SELECT ID, FileName, FilePath
        FROM TM_Images
        WHERE BibTags LIKE ? OR BibTags = ?
    """, (f'%{bib_number}%', bib_number))
    
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        # Extract thumbnail filename from FilePath
        thumbnail_name = os.path.basename(row[2])
        results.append({
            "ImageID": row[0],
            "FileName": row[1],
            "FilePath": row[2],
            "ThumbnailUrl": f"/images/{thumbnail_name}"
        })
    
    if not results:
        return {"message": f"No images found with BIB number: {bib_number}", "matches": []}
    
    return {"matches": results, "count": len(results)}


if __name__ == "__main__":
    uvicorn.run(service, host="0.0.0.0", port=8000)
