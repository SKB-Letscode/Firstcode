# Alternative: Deploy without Face Search (BIB Search Only)
# This removes face_recognition dependency to avoid memory issues

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sqlite3
import pickle

# Download files from S3 on startup (for Render deployment)
print("Checking for S3 files...")
if not os.path.exists(os.getenv('DB_FOLDER', '/opt/render/project/src/DB') + '/1_ImageDB.sqlite'):
    print("DB files not found locally, downloading from S3...")
    from app.s3_downloader import download_from_s3
    download_from_s3()
else:
    print("DB files found locally, skipping S3 download")

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
THUMBNAILS_FOLDER = os.path.join(workspace_root, "Images")

# DB paths
from app.dbconnector import local_db_path

# Print paths for debugging on Render
print(f"\n=== Path Configuration ===")
print(f"Workspace root: {workspace_root}")
print(f"Thumbnails folder: {THUMBNAILS_FOLDER}")
print(f"DB path: {local_db_path}")
print(f"DB exists: {os.path.exists(local_db_path)}")
print(f"Images folder exists: {os.path.exists(THUMBNAILS_FOLDER)}")
if os.path.exists(THUMBNAILS_FOLDER):
    print(f"Images folder contents: {len(os.listdir(THUMBNAILS_FOLDER))} items")
print(f"========================\n")

service = FastAPI(title="Face Search API - BIB Only")

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
        "mode": "BIB search only",
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
    logo_path = os.path.join(workspace_root, "Images", "support", "SiS_logo_Banner.png")
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
async def search_face(file: UploadFile = File(...), top_k: int = 5):
    """Face search disabled in this deployment due to memory constraints"""
    return {
        "error": "Face search temporarily disabled. Please upgrade to Starter plan for full functionality.",
        "message": "Use BIB search instead"
    }

@service.post("/search-bib")
async def search_bib(request: BibSearchRequest):
    """Search images by BIB number"""
    try:
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
            results.append({
                "FileName": filename,
                "FilePath": filepath,
                "BibTags": bibtags,
                "ThumbnailUrl": f"/images/{filename}"
            })
        
        return {"matches": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e), "matches": []}

@service.get("/events")
async def get_events():
    """Get list of all events"""
    print(f"\n=== /events endpoint called ===")
    print(f"DB path: {local_db_path}")
    print(f"DB exists: {os.path.exists(local_db_path)}")
    
    try:
        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TM_Images'")
        table_exists = cursor.fetchone()
        print(f"TM_Images table exists: {table_exists is not None}")
        
        if not table_exists:
            conn.close()
            return {"error": "TM_Images table not found", "events": []}
        
        cursor.execute("SELECT DISTINCT EventID FROM TM_Images ORDER BY EventID")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} events: {rows}")
        
        events = [{"EventID": row[0], "EventName": f"Event {row[0]}"} for row in rows]
        conn.close()
        
        print(f"Returning events: {events}")
        return {"events": events}
    except Exception as e:
        print(f"Error in /events: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "events": []}

@service.post("/event-images")
async def get_event_images(request: EventImagesRequest):
    """Get paginated images for a specific event"""
    try:
        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM TM_Images WHERE EventID = ?", (request.event_id,))
        total = cursor.fetchone()[0]
        
        # Get paginated results
        cursor.execute("""
            SELECT FileName, FilePath, BibTags
            FROM TM_Images
            WHERE EventID = ?
            ORDER BY FileName
            LIMIT ? OFFSET ?
        """, (request.event_id, request.limit, request.offset))
        
        matches = cursor.fetchall()
        conn.close()
        
        results = []
        for match in matches:
            filename, filepath, bibtags = match
            results.append({
                "FileName": filename,
                "FilePath": filepath,
                "BibTags": bibtags,
                "ThumbnailUrl": f"/images/{filename}"
            })
        
        return {
            "matches": results,
            "total": total,
            "offset": request.offset,
            "limit": request.limit,
            "hasMore": (request.offset + request.limit) < total
        }
    except Exception as e:
        return {"error": str(e), "matches": [], "total": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(service, host="0.0.0.0", port=8000)
