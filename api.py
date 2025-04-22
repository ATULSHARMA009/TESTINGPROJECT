from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
import httpx
import io
import os
from image_processor import ImageProcessor
from PIL import Image
import asyncio
import tempfile
from typing import List, Optional
from contextlib import asynccontextmanager

# Create a temporary directory for processed images
TEMP_DIR = "temp_images"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Create temporary directory
    os.makedirs(TEMP_DIR, exist_ok=True)
    yield
    # Shutdown: Clean up temporary files
    for file in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, file))
        except:
            pass

app = FastAPI(title="Image Processing API", lifespan=lifespan)
processor = ImageProcessor()

# Sample images for testing
SAMPLE_IMAGES = [
    {
        "id": 1,
        "title": "Sample Nature Image",
        "url": "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=600",
        "thumbnailUrl": "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=150"
    },
    {
        "id": 2,
        "title": "Sample Portrait",
        "url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=600",
        "thumbnailUrl": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150"
    },
    {
        "id": 3,
        "title": "Sample Architecture",
        "url": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=600",
        "thumbnailUrl": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=150"
    }
]

async def fetch_image_from_url(url: str) -> bytes:
    """Fetch image from URL and return bytes."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Image not found")
        return response.content

@app.get("/")
async def root():
    """Root endpoint showing API information."""
    return {
        "title": "Image Processing API",
        "version": "1.0",
        "endpoints": [
            "/photos - List available sample images",
            "/process/{photo_id}/remove-background - Remove image background",
            "/process/{photo_id}/enhance - Enhance image quality",
            "/process/{photo_id}/resize - Resize image"
        ]
    }

@app.get("/photos")
async def list_photos(
    limit: int = Query(10, description="Number of photos to return")
):
    """List available sample photos."""
    return SAMPLE_IMAGES[:limit]

@app.get("/process/{photo_id}/remove-background")
async def remove_background(photo_id: int):
    """Remove background from a specific photo."""
    # Find photo in sample images
    photo = next((p for p in SAMPLE_IMAGES if p["id"] == photo_id), None)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Download image
    image_bytes = await fetch_image_from_url(photo["thumbnailUrl"])
    
    # Save original image temporarily
    temp_input = os.path.join(TEMP_DIR, f"input_{photo_id}.jpg")
    temp_output = os.path.join(TEMP_DIR, f"output_{photo_id}.png")
    
    with open(temp_input, "wb") as f:
        f.write(image_bytes)
    
    # Process image
    if processor.remove_background(temp_input, temp_output):
        return FileResponse(temp_output, media_type="image/png")
    else:
        raise HTTPException(status_code=500, detail="Failed to process image")

@app.get("/process/{photo_id}/enhance")
async def enhance_image(photo_id: int):
    """Enhance a specific photo."""
    # Find photo in sample images
    photo = next((p for p in SAMPLE_IMAGES if p["id"] == photo_id), None)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Download image
    image_bytes = await fetch_image_from_url(photo["thumbnailUrl"])
    
    # Save original image temporarily
    temp_input = os.path.join(TEMP_DIR, f"input_{photo_id}.jpg")
    temp_output = os.path.join(TEMP_DIR, f"enhanced_{photo_id}.jpg")
    
    with open(temp_input, "wb") as f:
        f.write(image_bytes)
    
    # Process image
    if processor.enhance_quality(temp_input, temp_output):
        return FileResponse(temp_output, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=500, detail="Failed to process image")

@app.get("/process/{photo_id}/resize")
async def resize_image(
    photo_id: int,
    width: Optional[int] = Query(None, description="New width"),
    height: Optional[int] = Query(None, description="New height")
):
    """Resize a specific photo."""
    if width is None and height is None:
        raise HTTPException(status_code=400, detail="Either width or height must be specified")
    
    # Find photo in sample images
    photo = next((p for p in SAMPLE_IMAGES if p["id"] == photo_id), None)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Download image
    image_bytes = await fetch_image_from_url(photo["thumbnailUrl"])
    
    # Save original image temporarily
    temp_input = os.path.join(TEMP_DIR, f"input_{photo_id}.jpg")
    temp_output = os.path.join(TEMP_DIR, f"resized_{photo_id}.jpg")
    
    with open(temp_input, "wb") as f:
        f.write(image_bytes)
    
    # Process image
    if processor.resize_without_distortion(temp_input, temp_output, width, height):
        return FileResponse(temp_output, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=500, detail="Failed to process image")

@app.get("/photos/{photo_id}/view")
async def view_photo(photo_id: int):
    """View a specific photo directly."""
    # Find photo in sample images
    photo = next((p for p in SAMPLE_IMAGES if p["id"] == photo_id), None)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Download image
    image_bytes = await fetch_image_from_url(photo["url"])
    
    # Create a temporary file to serve
    temp_file = os.path.join(TEMP_DIR, f"view_{photo_id}.jpg")
    with open(temp_file, "wb") as f:
        f.write(image_bytes)
    
    return FileResponse(temp_file, media_type="image/jpeg") 