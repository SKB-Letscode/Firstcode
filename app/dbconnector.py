#====================================================================================
# Author: Sara 
# Created on: 21 Nov 2025
# Brief: Keep all DB related constants etc in one place for easy management.
# Precondition :
#====================================================================================

import os
import sqlite3

# Data configuration may get changed later
EventID = 1

DB_FILE = "ImageDB.sqlite"
INDEX_FILE = "faiss_face_index.bin"
META_FILE = "face_metadata.pkl"

# AWS S3 Config
bucket_name = os.getenv('S3_BUCKET_NAME', "sara-s3-bucket")
db_subfolder = r"FMF/SQLiteDB"  # S3 subfolder where DB is stored
s3_imagefolder_prefix = r"FMF/FMFImages/"  # S3 image folder folder path



# Local file names
# local_db_folder = os.getenv('DB_FOLDER', r"C:\Work\FMF\DB")  # Local folder to store DB
local_db_folder = os.getenv('DB_FOLDER', r"C:\Work\Data\Events\\" + str(EventID) + r"\DB")  # Local folder to store DB
local_events_db_folder = os.getenv('DB_FOLDER', r"C:\Work\Data\Events")  # Local folder to store only events details
DB_FILE = str(EventID) +"_ImageDB.sqlite"
SIS_EVENTS_DB_FILE = "SIS_Events_DB.sqlite"
INDEX_FILE = str(EventID) +"_faiss_face_index.bin"
META_FILE = str(EventID) +"_face_metadata.pkl"

# Full local paths
local_db_path = os.path.join(local_db_folder, DB_FILE)
local_sis_events_db_path = os.path.join(local_events_db_folder, SIS_EVENTS_DB_FILE)
local_index_path = os.path.join(local_db_folder, INDEX_FILE)
local_meta_path = os.path.join(local_db_folder, META_FILE)

# Local sub folders 
LOCAL_THUMBNAIL_FOLDER = os.getenv('IMAGE_FOLDER', r"C:\Work\Data\Events\\" + str(EventID) + r"\Thumbnails")
LOCAL_IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', r"C:\Work\Data\Events\\" + str(EventID) + r"\Images")

# Initialize DB
def init_db():
    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TM_Images (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EventID INTEGER,
            FileName TEXT,
            FilePath TEXT,
            BibTags TEXT
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
