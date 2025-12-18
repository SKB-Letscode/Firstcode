
#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: This script is to expose apis for uplaod / search images 
#           by end users can be used by any other cluient apps/pages.
# 18-Dec-2025 : Added event-images APIs and pagination support
# uvicorn app.server.api_services:service --reload
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

# Request model for Event images with pagination
class EventImagesRequest(BaseModel):
    event_id: int
    offset: int = 0
    limit: int = 10

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
    logo_path = os.path.join(workspace_root, "Images", "support", "SiS_logo_Banner.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    return {"error": "Logo not found", "path": logo_path}

@service.get("/download-icon")
def get_download_icon():
    """Serve the download icon image"""
    icon_path = os.path.join(workspace_root, "Images", "support", "download_icon.png")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    return {"error": "Download icon not found", "path": icon_path}

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

# -----------------------------------------------------------------------------------------------------
# Service to get list of active events
# Returns all events where Status = 'Active'
# -----------------------------------------------------------------------------------------------------

@service.get("/events")
async def get_active_events():
    """
    Get list of all active events.
    
    Returns:
        JSON with list of active events (ID, Name, Date, Organizer, Venue, TotalImages)
    """
    results = []
    
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ID, Name, Date, Organizer, Venue, TotalImages
        FROM TM_Events
        WHERE Atatus = 'Active'
        ORDER BY Date DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        results.append({
            "ID": row[0],
            "Name": row[1],
            "Date": row[2],
            "Organizer": row[3],
            "Venue": row[4],
            "TotalImages": row[5]
        })
    
    return {"events": results, "count": len(results)}

# -----------------------------------------------------------------------------------------------------
# Service to get images for a specific event with pagination
# Receives event_id, offset, and limit for pagination
# -----------------------------------------------------------------------------------------------------

@service.post("/event-images")
async def get_event_images(request: EventImagesRequest):
    """
    Get images for a specific event with pagination.
    
    Args:
        request: EventImagesRequest containing event_id, offset, and limit
    
    Returns:
        JSON with list of images for the event and pagination info
    """
    event_id = request.event_id
    offset = request.offset
    limit = request.limit
    
    results = []
    
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    
    # Get total count for this event
    cursor.execute("""
        SELECT COUNT(*) FROM TM_Images WHERE EventID = ?
    """, (event_id,))
    total_count = cursor.fetchone()[0]
    
    # Get paginated images
    cursor.execute("""
        SELECT ID, FileName, FilePath
        FROM TM_Images
        WHERE EventID = ?
        ORDER BY ID
        LIMIT ? OFFSET ?
    """, (event_id, limit, offset))
    
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
    
    return {
        "matches": results,
        "count": len(results),
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + len(results)) < total_count
    }


if __name__ == "__main__":
    uvicorn.run(service, host="0.0.0.0", port=8000)
