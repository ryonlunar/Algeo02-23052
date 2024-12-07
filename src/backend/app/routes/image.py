from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter()

# Update directory paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, 'album_images')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

# Debug print paths
print(f"Image Route - BASE_DIR: {BASE_DIR}")
print(f"Image Route - IMAGE_FOLDER: {IMAGE_FOLDER}")
print(f"Image Route - TEMP_DIR: {TEMP_DIR}")

os.makedirs(TEMP_DIR, exist_ok=True)
print(f"Image Route - Created/checked TEMP_DIR")

def extract_features(image_path: str) -> np.ndarray:
    """Extract image features using HSV color histograms."""
    try:
        print(f"Reading image from: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        print("Converting to HSV")
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        print("Calculating histograms")
        h_hist = cv2.calcHist([hsv], [0], None, [32], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [32], [0, 256])
        v_hist = cv2.calcHist([hsv], [2], None, [32], [0, 256])
        
        print("Normalizing histograms")
        h_hist = cv2.normalize(h_hist, h_hist, 0, 1, cv2.NORM_MINMAX)
        s_hist = cv2.normalize(s_hist, s_hist, 0, 1, cv2.NORM_MINMAX)
        v_hist = cv2.normalize(v_hist, v_hist, 0, 1, cv2.NORM_MINMAX)
        
        features = np.concatenate([h_hist, s_hist, v_hist]).flatten()
        print(f"Features extracted, shape: {features.shape}")
        return features
    
    except Exception as e:
        print(f"Error in extract_features: {str(e)}")
        # Handle the exception, e.g., return a default feature vector or skip the file
        return np.zeros(96)

def find_similar_images(query_features: np.ndarray, image_folder: str, n: int = 10):
    """Find similar images using cosine similarity."""
    similarities = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    
    try:
        print(f"Scanning folder: {image_folder}")
        files = os.listdir(image_folder)
        print(f"Found {len(files)} files in folder")
        
        for filename in files:
            if os.path.splitext(filename)[1].lower() in valid_extensions:
                print(f"Processing {filename}")
                image_path = os.path.join(image_folder, filename)
                features = extract_features(image_path)
                
                similarity = cosine_similarity(
                    query_features.reshape(1, -1), 
                    features.reshape(1, -1)
                )[0][0]
                
                similarities.append((filename, similarity))
                print(f"Similarity with {filename}: {similarity:.4f}")
        
        if not similarities:
            raise ValueError("No valid images found for comparison")
            
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_n = similarities[:n]
        filenames, scores = zip(*top_n)
        
        print(f"Found {len(filenames)} similar images")
        return list(filenames), list(scores)
    
    except Exception as e:
        print(f"Error in find_similar_images: {str(e)}")
        raise ValueError(f"Failed to find similar images: {str(e)}")

@router.post("/api/retrieve")
async def retrieve_images(file: UploadFile = File(...)):
    """Handle image retrieval requests."""
    try:
        print(f"\n=== Starting image retrieval for {file.filename} ===")
        
        # Validate file
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in valid_extensions:
            print(f"Invalid file extension: {file_ext}")
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please use JPG, JPEG, PNG, or GIF"
            )
        
        # Save temporary file
        temp_path = os.path.join(TEMP_DIR, file.filename)
        print(f"Saving temporary file to: {temp_path}")
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            print("Extracting features from uploaded image")
            query_features = extract_features(temp_path)
            
            print("Finding similar images")
            similar_images, similarity_scores = find_similar_images(
                query_features, 
                IMAGE_FOLDER,
                n=len(IMAGE_FOLDER)
            )
            
            print(f"Found {len(similar_images)} similar images")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "similar_images": similar_images,
                    "similarity_scores": [float(score) for score in similarity_scores]
                }
            )
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                print("Temporary file deleted")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error in retrieve_images: {error_msg}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": error_msg
            }
        )