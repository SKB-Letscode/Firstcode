#====================================================================================
# Author: Sara / Co Pilot 
# Created on: 21 Nov 2025
# Brief: Alternative: Deploy without Face Search (BIB Search Only)
#        This removes face_recognition dependency to avoid memory issues
# 18-Dec-2025 : Added event-images APIs and pagination support
# 24-Dec-2025 : Added face search feature with memory optimizations for Render Starter
# uvicorn app.server.api_services_minimal:service --reload
#====================================================================================

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sqlite3
import pickle
import numpy as np
import faiss
import hashlib

# Data configuration may get changed later
# EventID = 1

# Download files from S3 on startup (for Render deployment)
# # Comented starts
# print("Checking for S3 files...")
# if not os.path.exists(os.getenv('DB_FOLDER', '/opt/render/project/src/DB') + '/1_ImageDB.sqlite'):
#     print("DB files not found locally, downloading from S3...")
#     from app.s3_downloader import download_from_s3
#     download_from_s3()
# else:
#     print("DB files found locally, skipping S3 download")

# # Comented Ends
# Request model for BIB search
class BibSearchRequest(BaseModel):
    bib_number: str
    event_id: int = 0

# Request model for Event images with pagination
class EventImagesRequest(BaseModel):
    event_id: int
    offset: int = 0
    limit: int = 10

# Base image location for thumbnails
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IMAGES_BASE_FOLDER = os.getenv('IMAGE_FOLDER', r"C:\Work\FMF\Data\Events")
THUMBNAILS_FOLDER = os.path.join(workspace_root, "Images")

# Local sub folders - do not assume a single EventID at module import time.
# Keep a global thumbnails folder (used by /images/*). For event-specific
# folders use the helper functions below which compute paths using the
# configured IMAGES_BASE_FOLDER or the environment `IMAGE_FOLDER`.
THUMBNAILS_FOLDER = os.getenv('IMAGE_FOLDER', os.path.join(workspace_root, "Images"))
LOCAL_IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', os.path.join(workspace_root, "Images"))


def event_thumbnails_path(event_id: int):
    """Return the thumbnails folder path for a given event_id."""
    base = os.getenv('IMAGE_FOLDER', IMAGES_BASE_FOLDER)
    return os.path.join(base, str(event_id), "Thumbnails")


def event_images_path(event_id: int):
    """Return the images folder path for a given event_id."""
    base = os.getenv('IMAGE_FOLDER', IMAGES_BASE_FOLDER)
    return os.path.join(base, str(event_id), "Images")


# DB paths
from app.dbconnector import (
    local_db_path,
    local_index_path,
    local_meta_path,
    local_sis_events_db_path,
    LOCAL_THUMBNAIL_FOLDER,
    local_events_db_folder,
    INDEX_FILE,
    META_FILE,
)

# Print paths for debugging on Render
print(f"\n=== Path Configuration ===")
print(f"Workspace root: {workspace_root}")
print(f"Thumbnails folder: {THUMBNAILS_FOLDER}")
print(f"DB path: {local_db_path}")
print(f"DB exists: {os.path.exists(local_db_path)}")
print(f"Index path: {local_index_path}")
print(f"Index exists: {os.path.exists(local_index_path)}")
print(f"Meta path: {local_meta_path}")
print(f"Meta exists: {os.path.exists(local_meta_path)}")
print(f"Images folder exists: {os.path.exists(THUMBNAILS_FOLDER)}")
if os.path.exists(THUMBNAILS_FOLDER):
    print(f"Images folder contents: {len(os.listdir(THUMBNAILS_FOLDER))} items")
print(f"========================\n")

# Determine if default (module-level) index files exist
FACE_SEARCH_ENABLED = os.path.exists(local_index_path) and os.path.exists(local_meta_path)

# Per-event index cache: maps event_id -> { 'index': faiss_index, 'face_ids': list }
event_index_cache = {}

def _event_db_folder(event_id: int):
    """Return the event-specific DB folder (e.g. <events_root>/<event_id>/DB)."""
    return os.path.join(local_events_db_folder, str(event_id), "DB")

def load_event_index(event_id: int):
    """Load and cache FAISS index + metadata for a given event_id.

    Returns (index, face_ids) or raises Exception on failure.
    """
    if event_id in event_index_cache:
        return event_index_cache[event_id]['index'], event_index_cache[event_id]['face_ids']

    folder = _event_db_folder(event_id)
    idx_path = os.path.join(folder, INDEX_FILE)
    meta_path = os.path.join(folder, META_FILE)

    if not os.path.exists(idx_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(f"Index/meta not found for event {event_id}: {idx_path}, {meta_path}")

    # Read index and metadata
    idx = faiss.read_index(idx_path)
    with open(meta_path, 'rb') as f:
        fids = pickle.load(f)

    event_index_cache[event_id] = { 'index': idx, 'face_ids': fids }
    return idx, fids

def preload_all_event_indices():
    """Load indices for all events listed in the SIS events DB.

    This reads `TM_Events.ID` from `local_sis_events_db_path` and attempts
    to load an index for each event. Successfully-loaded event IDs are
    stored in `event_index_cache` by `load_event_index`.
    """
    global FACE_SEARCH_ENABLED
    loaded = []
    try:
        if not os.path.exists(local_sis_events_db_path):
            print(f"SIS events DB not found at {local_sis_events_db_path}; skipping preload")
            FACE_SEARCH_ENABLED = len(event_index_cache) > 0 or (os.path.exists(local_index_path) and os.path.exists(local_meta_path))
            return loaded

        conn = sqlite3.connect(local_sis_events_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM TM_Events")
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            try:
                eid = int(r[0])
            except Exception:
                print(f"Skipping invalid event id: {r}")
                continue

            try:
                load_event_index(eid)
                loaded.append(eid)
                print(f"Loaded FAISS index for event {eid}")
            except Exception as e:
                print(f"Could not load index for event {eid}: {e}")

    except Exception as e:
        print(f"Error while preloading event indices: {e}")

    FACE_SEARCH_ENABLED = len(event_index_cache) > 0 or (os.path.exists(local_index_path) and os.path.exists(local_meta_path))
    print(f"Preload complete. Loaded indices for events: {loaded}")
    return loaded


# Create FastAPI service early so decorators can reference it
service = FastAPI(title="Face Search API - Full Featured")


@service.on_event("startup")
def _startup_preload_indices():
    print("Startup: preloading FAISS indices for all events...")
    preload_all_event_indices()

# Configuration for face search
MAX_DIM = 800  # Resize images to reduce memory usage
DISTANCE_THRESHOLD = 0.19  # Only return matches with distance <= this value

# Utility: compare files by MD5 to detect placeholder/logo duplicates
def file_md5(path, block_size=65536):
    """Return MD5 hash of a file (used to detect placeholder/logo files)."""
    h = hashlib.md5()
    try:
        with open(path, 'rb') as fh:
            for chunk in iter(lambda: fh.read(block_size), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def is_same_as_placeholder(path):
    """Return True if the given file is byte-identical to the app placeholder/logo."""
    placeholder = os.path.join(workspace_root, "Images", "support", "SIS_Logo_Black_Text.png")
    if not (path and os.path.exists(path) and os.path.exists(placeholder)):
        return False
    md1 = file_md5(path)
    md2 = file_md5(placeholder)
    return (md1 is not None and md2 is not None and md1 == md2)


# Enable CORS
service.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Web directory
app_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
web_folder = os.path.join(app_folder, "web")
if os.path.exists(web_folder):
    service.mount("/web", StaticFiles(directory=web_folder), name="web")

@service.get("/")
def read_root():
    """Serve the web application"""
    app_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    web_folder = os.path.join(app_folder, "web")
    index_path = os.path.join(web_folder, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Web app not found. Looking for: {index_path}"}

@service.get("/health")
def health_check():
    """Health check with path verification"""
    return {
        "status": "ok",
        "mode": "Full featured (Face + BIB search)" if FACE_SEARCH_ENABLED else "BIB search only",
        "face_search_enabled": FACE_SEARCH_ENABLED,
        "loaded_event_indices": list(event_index_cache.keys()),
        "loaded_count": len(event_index_cache),
        "db_path": local_db_path,
        "db_exists": os.path.exists(local_db_path),
        "images_folder": THUMBNAILS_FOLDER,
        "images_exists": os.path.exists(THUMBNAILS_FOLDER),
        "workspace_root": workspace_root
    }

@service.get("/images/{filename}")
def get_image(filename: str):
    """Serve thumbnail images"""
    image_path = os.path.join(THUMBNAILS_FOLDER, filename)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found", "path": image_path}

@service.get("/logo")
def get_logo():
    """Serve the logo image"""
    logo_path = os.path.join(workspace_root, "Images", "support", "SIS_Logo_Black_Text.png")
    print(f"\n=== /logo endpoint called ===")
    print(f"Logo path: {logo_path}")
    print(f"Logo exists: {os.path.exists(logo_path)}")
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    # List what's in the support folder
    support_folder = os.path.join(workspace_root, "Images", "support")
    if os.path.exists(support_folder):
        print(f"Support folder contents: {os.listdir(support_folder)}")
    return {"error": "Logo not found", "path": logo_path}

@service.get("/download-icon")
def get_download_icon():
    """Serve the download icon image"""
    icon_path = os.path.join(workspace_root, "Images", "support", "download_icon.png")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    return {"error": "Download icon not found", "path": icon_path}

@service.post("/search-face")
async def search_face(file: UploadFile = File(...), top_k: int = 5, event_id: int = 1):
    """
    Search for faces in uploaded image
    
    Args:
        file: Uploaded image file containing a face
        top_k: Number of top matches to return (default: 5)
    
    Returns:
        JSON with list of matching images
    """
    # Load (or get cached) FAISS index + metadata for the requested event
    try:
        event_index, event_face_ids = load_event_index(event_id)
    except Exception as e:
        return {
            "error": "Face search is not available for this event",
            "message": str(e),
            "matches": []
        }
    
    temp_path = None
    try:
        # Import required libraries
        import face_recognition
        from PIL import Image
        import io
        
        # Debug: Print file details
        print(f"\n=== Face Search Request ===")
        print(f"Filename: {file.filename}")
        print(f"Content-Type: {file.content_type}")
        
        # Read uploaded file content
        content = await file.read()
        content_len = len(content)
        
        print(f"Received {content_len} bytes")
        
        # Verify content was received and is a reasonable size
        if not content or content_len == 0:
            return {
                "error": "Empty file received",
                "message": "The uploaded file appears to be empty",
                "matches": []
            }
        
        # Check if file is suspiciously small (likely not a real image)
        if content_len < 1000:  # Real JPG/PNG images are typically > 1KB
            return {
                "error": "File too small",
                "message": f"Received only {content_len} bytes. Please ensure you're uploading a valid image file (not just a filename or reference).",
                "matches": []
            }
        
        # Try to open and process image directly from bytes
        try:
            # Open image from bytes
            img_bytes = io.BytesIO(content)
            pil_img = Image.open(img_bytes)
            print(f"✓ Image opened: format={pil_img.format}, size={pil_img.size}, mode={pil_img.mode}")
            
            # Convert to RGB if needed
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
                print(f"✓ Converted to RGB")
            
            # Resize to reduce memory usage
            pil_img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
            print(f"✓ Resized to max {MAX_DIM}px")
            
            # Convert to numpy array for face_recognition
            img = np.array(pil_img)
            print(f"✓ Converted to numpy array: shape={img.shape}")
            
        except Exception as e:
            print(f"✗ Failed to process image from bytes: {e}")
            return {
                "error": f"Invalid image file: {str(e)}",
                "message": "Could not open the uploaded file. Please ensure it's a valid JPG or PNG image.",
                "matches": []
            }
        
        # Extract face encodings
        uploaded_faces = face_recognition.face_encodings(img)
        
        if len(uploaded_faces) == 0:
            return {
                "error": "No face detected in the uploaded image",
                "message": "Please upload a clear image with a visible face",
                "matches": []
            }
        
        results = []
        
        # Search for each detected face
        for face_emb in uploaded_faces:
            face_emb = np.expand_dims(face_emb.astype('float32'), axis=0)
            distances, indices = event_index.search(face_emb, top_k)
            
            for j, i in enumerate(indices[0]):
                dist = float(distances[0][j])
                
                # Only include matches at or below the threshold
                if dist <= DISTANCE_THRESHOLD:
                    matched_face_id = event_face_ids[i]
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
                        # Use FileName directly (not FilePath which contains full Windows path)
                        file_name = img_info[0]  # This is just the filename like "SKB_4219.JPG"
                        results.append({
                            "FileName": file_name,
                            "FilePath": img_info[1],
                            "ThumbnailUrl": f"/images/{file_name}",
                            "Distance": dist
                        })
        
        return {"matches": results}
    
    except Exception as e:
        return {
            "error": f"Face search failed: {str(e)}",
            "matches": []
        }
    
    finally:
        # Clean up temp file if it was created
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                print(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                print(f"Failed to remove temp file {temp_path}: {e}")
# Search based on the Bib numer entered by the user from the selecetd  event
@service.post("/search-bib")
async def search_bib(request: BibSearchRequest):
    """Search images by BIB number"""
    try:
        # Ensure event_id is present (model has default=1)
        event_id = int(request.event_id)
        local_db_folder = os.getenv('DB_FOLDER', r"C:\\Work\\FMF\\Data\\Events\\" + str(event_id) + r"\DB")  # Local folder to store DB
        DB_FILE = "ImageDB.sqlite"
        local_db_path = os.path.join(local_db_folder, DB_FILE)
        if not os.path.exists(local_db_path):
            return {"error": f"Image DB not found for event {event_id}", "matches": []}
        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT FileName, FilePath, BibTags
            FROM TM_Images
            WHERE BibTags LIKE ?
        """, (f"%{request.bib_number}%",))
        
        matches = cursor.fetchall()
        conn.close()
        results = []
        for match in matches:
            filename, filepath, bibtags = match
            # Use the basename of FilePath if possible (this should map to files inside Events/<id>/Thumbnails or Images)
            thumb_name = os.path.basename(filepath) if filepath else filename
            
            # Return proper URL path instead of filesystem path
            thumbnail_url = f"/event-image/{event_id}/{thumb_name}"
            
            results.append({
                "FileName": filename,
                "FilePath": filepath,
                "BibTags": bibtags,
                "ThumbnailUrl": thumbnail_url
            })
            print(f"/search-bib: Found match for BIB {request.bib_number} - file: {thumbnail_url}")

        return {"matches": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e), "matches": []}

@service.get("/events")
async def get_events():
    """Get list of all events from SIS_EVENTS_DB . TM_Events table"""
    print(f"\n=== /events endpoint called ===")
    print(f"DB path: {local_sis_events_db_path}")
    print(f"DB exists: {os.path.exists(local_sis_events_db_path)}")
    
    try:
        conn = sqlite3.connect(local_sis_events_db_path)
        cursor = conn.cursor()
        
        # Check if TM_Events table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TM_Events'")
        if not cursor.fetchone():
            conn.close()
            return {"error": "TM_Events table not found", "events": []}

        # Determine available columns so we return Organizer/Venue if present
        cursor.execute("PRAGMA table_info('TM_Events')")
        cols = [r[1] for r in cursor.fetchall()]
        select_cols = [c for c in ["ID","Name","Date","Organizer","Venue","TotalImages"] if c in cols]

        cursor.execute(f"SELECT {', '.join(select_cols)} FROM TM_Events ORDER BY ID")
        rows = cursor.fetchall()

        events = []
        for row in rows:
            ev = {}
            for i, col in enumerate(select_cols):
                ev[col] = row[i]
            events.append(ev)

        conn.close()
        print(f"Returning events: {events}")
        return {"events": events}
    except Exception as e:
        print(f"Error in /events: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "events": []}

# This method is cleaned and simplified to work : Sara
@service.get("/event-thumbnail/{event_id}")
def get_event_thumbnail(event_id: int):
    try:
        # sanitize event_id
        event_id = int(event_id)
        thumbnail_image = os.path.join(event_thumbnails_path(event_id), "EventThumbnail.JPG")
        print (f"SKB - Looking for thumbnail in folder: {thumbnail_image}")
        if os.path.exists(thumbnail_image):
            return FileResponse(thumbnail_image)

        # fallback to placeholder if event thumbnail missing
        placeholder = os.path.join(workspace_root, "Images", "support", "SIS_Logo_Black_Text.png")
        if os.path.exists(placeholder):
            return FileResponse(placeholder)
        return {"error": f"Thumbnail not available for event {event_id}", "path": thumbnail_image}
    except Exception as e:
        print(f"Error serving thumbnail for event {event_id}: {e}")
        return {"error": f"Thumbnail not available for event {event_id}"}

# GEt all images based on the selecetd event
@service.post("/event-images")
async def get_event_images(request: EventImagesRequest):
    """Get paginated images for a specific event"""
    try:

        local_db_folder = os.getenv('DB_FOLDER', r"C:\Work\FMF\Data\Events\\" + str(request.event_id) + r"\DB")  # Local folder to store DB
        DB_FILE = "ImageDB.sqlite"
        local_db_path = os.path.join(local_db_folder, DB_FILE)

        print(f"SKB - local_db_file is {local_db_path}")

        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()

        # Get total images for this event
        cursor.execute("SELECT COUNT(*) FROM TM_Images")
        total = cursor.fetchone()[0]
        print(f"/event-images: event_id={request.event_id} matched={total}")

        # Get paginated results for this event
        cursor.execute("""
            SELECT FileName, FilePath, BibTags
            FROM TM_Images
            ORDER BY FileName
            LIMIT ? OFFSET ?
        """, (request.limit, request.offset))
        matches = cursor.fetchall()
        conn.close()

        results = []

        print(f"SKB Workspace root is " + workspace_root)

        for match in matches:
            filename, filepath, bibtags = match
            # Use the basename of FilePath if possible (this should map to files inside Events/<id>/Thumbnails or Images)
            thumb_name = os.path.basename(filepath) if filepath else filename

            # Prefer event-specific thumbnails/images if they exist; otherwise prefer global thumbnails
            event_thumb = os.path.join(event_thumbnails_path(request.event_id), thumb_name)

            print(f"event_thumb is {event_thumb}")

            event_image = os.path.join(event_images_path(request.event_id), thumb_name)

            chosen_source = None
            # Prefer event-specific thumbnail/image if present and not identical to placeholder
            if os.path.exists(event_thumb) and not is_same_as_placeholder(event_thumb):
                thumbnail_url = f"/event-image/{request.event_id}/{thumb_name}"
                chosen_source = 'event:thumb'
            elif os.path.exists(event_image) and not is_same_as_placeholder(event_image):
                thumbnail_url = f"/event-image/{request.event_id}/{thumb_name}"
                chosen_source = 'event:image'
            else:
                # Check global thumbnails folders
                global_thumb_path_1 = os.path.join(THUMBNAILS_FOLDER, thumb_name) if THUMBNAILS_FOLDER else None
                global_thumb_path_2 = os.path.join(LOCAL_THUMBNAIL_FOLDER, thumb_name) if LOCAL_THUMBNAIL_FOLDER else None

                if global_thumb_path_1 and os.path.exists(global_thumb_path_1) and not is_same_as_placeholder(global_thumb_path_1):
                    thumbnail_url = f"/images/{thumb_name}"
                    chosen_source = 'global:THUMBNAILS_FOLDER'
                elif global_thumb_path_2 and os.path.exists(global_thumb_path_2) and not is_same_as_placeholder(global_thumb_path_2):
                    thumbnail_url = f"/images/{thumb_name}"
                    chosen_source = 'global:LOCAL_THUMBNAIL_FOLDER'
                else:
                    # Fallback to event-image endpoint which itself will return a placeholder if the file is missing
                    thumbnail_url = f"/event-image/{request.event_id}/{thumb_name}"
                    chosen_source = 'placeholder'

            print(f"/event-images: file={thumb_name} source={chosen_source}")

            results.append({
                "FileName": filename,
                "FilePath": filepath,
                "BibTags": bibtags,
                "ThumbnailUrl": thumbnail_url
            })

        return {
            "matches": results,
            "total": total,
            "offset": request.offset,
            "limit": request.limit,
            "count": len(results),
            "hasMore": (request.offset + len(results)) < total
        }
    except Exception as e:
        print(f"Error in /event-images: {e}")
        return {"error": str(e), "matches": [], "total": 0}

@service.get("/event-image/{event_id}/{filename}")
def get_event_image(event_id: int, filename: str):
    """Serve an image thumbnail for a specific event from Events/<id>/Thumbnails or Events/<id>/Images"""
    # sanitize filename
    safe_name = os.path.basename(filename)

    thumbs_folder = event_thumbnails_path(event_id)
    images_folder = event_images_path(event_id)

    candidate = os.path.join(thumbs_folder, safe_name)
    if os.path.exists(candidate):
        return FileResponse(candidate)

    candidate = os.path.join(images_folder, safe_name)
    if os.path.exists(candidate):
        return FileResponse(candidate)

    # Fallback to placeholder
    placeholder = os.path.join(workspace_root, "Images", "support", "SIS_Logo_Black_Text.png")
    if os.path.exists(placeholder):
        return FileResponse(placeholder)

    return {"error": "Image not found", "path": candidate}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(service, host="0.0.0.0", port=8000)
