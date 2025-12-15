# Find My Photos - Web Application

A responsive web application for searching photos by face recognition or BIB number.

## Features

- 🔍 **Face Search**: Upload a selfie to find all photos containing your face
- 🏃 **BIB Search**: Search photos by runner's BIB number
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ⬇️ **Download**: Download individual photos directly from the results
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/ML**: 
  - Face Recognition (dlib)
  - FAISS (Facebook AI Similarity Search)
  - EasyOCR (for BIB detection)

## Setup & Running

### 1. Start the API Server

```bash
# Navigate to project root
cd C:\Work\FMF

# Activate virtual environment
venv\Scripts\activate

# Run the server
python -m uvicorn app.selfisearch.server.api_services:service --reload --host 0.0.0.0 --port 8000
```

### 2. Access the Web Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

### Search by Face
1. Click the "Search by Face" tab
2. Click the upload area or drag & drop your selfie
3. Click "Search Photos"
4. View matching photos in the gallery
5. Click the download button on any photo to save it

### Search by BIB
1. Click the "Search by BIB" tab
2. Enter the BIB number (e.g., "123")
3. Click "Search Photos"
4. View matching photos in the gallery
5. Click the download button on any photo to save it

## API Endpoints

### GET /
Serves the web application

### GET /health
Health check endpoint
```json
{"status": "ok"}
```

### POST /search-face
Search photos by uploaded face image

**Request:**
- `file`: Image file (multipart/form-data)
- `top_k`: Number of results to return (optional, default: 5)

**Response:**
```json
{
  "matches": [
    {
      "FileName": "IMG_001.jpg",
      "FilePath": "C:/Work/FMF/Images/IMG_001.jpg",
      "Distance": 0.12
    }
  ]
}
```

### POST /search-bib
Search photos by BIB number

**Request:**
```json
{
  "bib_number": "123"
}
```

**Response:**
```json
{
  "matches": [
    {
      "ImageID": 45,
      "FileName": "IMG_001.jpg",
      "FilePath": "C:/Work/FMF/Images/IMG_001.jpg"
    }
  ],
  "count": 1
}
```

## File Structure

```
app/selfisearch/server/
├── api_services.py          # FastAPI backend
├── static/
│   └── index.html          # Web application (single-file)
└── WEB_APP_README.md       # This file
```

## Troubleshooting

### Images not displaying
- Ensure image paths in the database are absolute paths
- Check that images exist at the specified file paths
- Browser security may block `file://` protocol URLs

### CORS errors
- CORS is enabled for all origins (`*`)
- If issues persist, check browser console for specific errors

### API not responding
- Verify the API server is running on port 8000
- Check that FAISS index and database files are present
- Review terminal logs for errors

## Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Responsive Breakpoints

- Desktop: > 768px (3-4 columns)
- Tablet: 480px - 768px (2-3 columns)
- Mobile: < 480px (1 column)

## Future Enhancements

- [ ] Image preview on hover
- [ ] Batch download multiple photos
- [ ] Advanced filters (date, location)
- [ ] Share photos via social media
- [ ] Dark mode support
- [ ] Photo tagging and favorites

## License

Private project - All rights reserved.
