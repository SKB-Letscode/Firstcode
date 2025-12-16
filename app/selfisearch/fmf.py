import os
import sqlite3
import numpy as np
from PIL import Image
import face_recognition
import faiss
import pickle


local_db_folder = r"C:\Work\FMF\DB"  # Local folder to store DB

# Local file names
DB_FILE = "ImageDB.sqlite"
INDEX_FILE = "faiss_face_index.bin"
META_FILE = "face_metadata.pkl"

# Full local paths
local_db_path = os.path.join(local_db_folder, DB_FILE)
local_index_path = os.path.join(local_db_folder, INDEX_FILE)
local_meta_path = os.path.join(local_db_folder, META_FILE)


# load index and metadata once
if os.path.exists(local_index_path):
    index = faiss.read_index(local_index_path)
else:
    index = faiss.IndexFlatL2(128)
if os.path.exists(local_meta_path):
    with open(local_meta_path, "rb") as f:
        face_ids = pickle.load(f)
else:
    face_ids = []

def load_and_resize_image(path, max_dim=800):
    """Load image with PIL and downscale while preserving aspect ratio."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = min(1.0, max_dim / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return np.array(img)

def preload_metadata():
    """Return mapping FaceID -> (FileName, FilePath) to avoid DB queries inside loop."""
    conn = sqlite3.connect(local_db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT FaceID, TM_Images.FileName, TM_Images.FilePath
        FROM TM_Faces
        JOIN TM_Images ON TM_Faces.ImageID = TM_Images.ID
    """)
    meta = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
    conn.close()
    return meta

def find_my_face(image_path, top_k=3, max_dim=800):
    # 1) Load & downscale to reduce CPU/time for detection/encoding
    img = load_and_resize_image(image_path, max_dim=max_dim)

    # 2) Fast detection (HOG) to get locations; pass locations to face_encodings to avoid double work
    locations = face_recognition.face_locations(img, model="hog")
    if not locations:
        return []

    # 3) Compute embeddings using known locations (faster) and minimal jitter
    encodings = face_recognition.face_encodings(img, known_face_locations=locations, num_jitters=1)
    if not encodings:
        return []

    # 4) Batch query FAISS (convert to float32)
    queries = np.vstack([e.astype("float32") for e in encodings])
    k = min(top_k, max(1, int(index.ntotal)))
    distances, indices = index.search(queries, k)

    # 5) Map indices -> face_ids -> metadata, using a preloaded map
    meta = preload_metadata()
    results = []
    for qi in range(len(encodings)):
        matches = []
        for nbr_rank, idx in enumerate(indices[qi]):
            if idx < 0 or idx >= len(face_ids):
                continue
            fid = face_ids[idx]
            if fid not in meta:
                continue
            filename, filepath = meta[fid]
            matches.append({
                "rank": nbr_rank,
                "FileName": filename,
                "FilePath": filepath,
                "Distance": float(distances[qi][nbr_rank])
            })
        results.append({"query_face_index": qi, "matches": matches})
    return results

if __name__ == "__main__":
    import sys, time
    if len(sys.argv) < 2:
        print("Usage: python find_my_face.py <image_path> [top_k]")
        sys.exit(1)
    t0 = time.time()
    img_path = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = find_my_face(img_path, top_k=top_k, max_dim=800)
    print("Elapsed:", time.time() - t0)
    print(out)