from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import os
import numpy as np
from PIL import Image
import shutil
from tempfile import NamedTemporaryFile
import time
import traceback

# Create router instance
router = APIRouter(tags=["image-retrieval"])

# Get the base directory path dynamically
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "album_images")

# Ensure the image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Debug information about directories
print(f"Current working directory: {os.getcwd()}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"IMAGE_FOLDER: {IMAGE_FOLDER}")
print(f"Image folder exists: {os.path.exists(IMAGE_FOLDER)}")
if os.path.exists(IMAGE_FOLDER):
    print(f"Images in folder: {os.listdir(IMAGE_FOLDER)}")

# [Semua fungsi helper tetap sama sampai image_retrieval_main]
def get_paths(folder):
    valid = ('.png', '.jpg', '.jpeg')
    paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(valid)]
    if not paths:
        raise ValueError(f"No valid images found in {folder}")
    return paths

def convert_grayscale(image_path):
    try:
        image = Image.open(image_path).convert('RGB')
        image_arr = np.array(image)
        
        if image_arr.shape[-1] == 4:
            image_arr = image_arr[:, :, :3]
            
        grayscale_arr = 0.2989 * image_arr[:, :, 0] + \
                        0.5870 * image_arr[:, :, 1] + \
                        0.1140 * image_arr[:, :, 2]
                        
        grayscale_image = Image.fromarray(grayscale_arr.astype('uint8'), mode="L")
        return grayscale_image
    except Exception as e:
        print(f"Error converting image to grayscale: {str(e)}")
        raise

def resize_image(image, width, height):
    try:
        return image.resize((width, height), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        raise

def flatten_image(image):
    try:
        image_arr = np.array(image)
        return image_arr.flatten()
    except Exception as e:
        print(f"Error flattening image: {str(e)}")
        raise

def image_processing(image_folder, width, height):
    if not os.path.exists(image_folder):
        raise ValueError(f"Image folder does not exist: {image_folder}")
        
    image_paths = get_paths(image_folder)
    if not image_paths:
        raise ValueError("No valid images found in the database")
    
    arr_images = []
    for path in image_paths:
        try:
            grayscaled_image = convert_grayscale(path)
            resized_image = resize_image(grayscaled_image, width, height)
            flattened_image = flatten_image(resized_image)
            arr_images.append(flattened_image)
        except Exception as e:
            print(f"Error processing image {path}: {str(e)}")
            continue
            
    if not arr_images:
        raise ValueError("No images could be processed")
        
    return np.array(arr_images)

def center_data(arr_images):
    try:
        mean_images = np.mean(arr_images, axis=0)
        arr_images_standardized = arr_images - mean_images
        return arr_images_standardized, mean_images
    except Exception as e:
        print(f"Error in center_data: {str(e)}")
        raise

def compute_PCA(arr_images_standardized, n_components):
    try:
        U, S, Ut = np.linalg.svd(arr_images_standardized, full_matrices=False)
        top_component = Ut[:n_components]
        projected = np.dot(arr_images_standardized, top_component.T)
        return projected, top_component
    except Exception as e:
        print(f"Error in compute_PCA: {str(e)}")
        raise

def preprocess_query(query_path, width, height):
    try:
        query_grayscale = convert_grayscale(query_path)
        query_resized = resize_image(query_grayscale, width, height)
        flatten_query = flatten_image(query_resized)
        return flatten_query
    except Exception as e:
        print(f"Error in preprocess_query: {str(e)}")
        raise

def projected_query(flattened_query, mean, top_components):
    try:
        center_query = flattened_query - mean
        query = np.dot(center_query, top_components.T)
        return query
    except Exception as e:
        print(f"Error in projected_query: {str(e)}")
        raise

def euclidean_distance(query_vector, image_vector):
    try:
        return np.linalg.norm(query_vector - image_vector)
    except Exception as e:
        print(f"Error in euclidean_distance: {str(e)}")
        raise

def image_retrieval_main(query_path, image_folder, n):
    try:
        print("Starting image retrieval process...")
        width, height = 300, 300
        
        print("Getting image paths...")
        images_path = get_paths(image_folder)
        
        print("Processing images...")
        images_array = image_processing(image_folder, width, height)
        
        print("Centering data...")
        standardized_vector, mean_images = center_data(images_array)
        
        print("Computing PCA...")
        n_component = 50
        projected_vector, top_components = compute_PCA(standardized_vector, n_component)
        
        print("Processing query image...")
        flattened_query = preprocess_query(query_path, width, height)
        proj_query = projected_query(flattened_query, mean_images, top_components)
        
        print("Computing distances...")
        distances = np.array([euclidean_distance(proj_query, projected_vector[i]) 
                            for i in range(len(projected_vector))])
        
        # Normalisasi distances ke similarity score (0-100%)
        max_distance = np.max(distances)
        similarity_scores = (1 - (distances / max_distance))
        
        # Sort berdasarkan similarity (tertinggi ke terendah)
        sort_indices = np.argsort(similarity_scores)[::-1]  # Reverse untuk descending
        top_indices = sort_indices[:n]
        
        top_similar = [images_path[i] for i in top_indices]
        top_similarities = similarity_scores[top_indices]
        
        return top_similar, top_similarities
        
    except Exception as e:
        print(f"Error in image_retrieval_main: {str(e)}")
        raise

@router.post("/image-search")
async def search_similar_images(file: UploadFile = File(...)):
    temp = None
    try:
        print("Starting image search process...")
        
        if not file.content_type.startswith('image/'):
            return JSONResponse(
                status_code=400,
                content={"error": "File must be an image"}
            )
        
        start_time = time.time()
        
        print("Creating temporary file...")
        temp = NamedTemporaryFile(delete=False)
        temp_path = temp.name
        temp.close()  # Close the file immediately
        
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        print(f"Temporary file created at: {temp_path}")
        print(f"Image folder path: {IMAGE_FOLDER}")
        
        print("Starting image retrieval main function...")
        top_similar, distances = image_retrieval_main(temp_path, IMAGE_FOLDER, n=len(IMAGE_FOLDER))
        
        print("Processing results...")
        # Perbaikan pembentukan relative paths
        relative_paths = [os.path.basename(path) for path in top_similar]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return JSONResponse(content={
            "similar_images": relative_paths,
            "similarity_scores": distances.tolist(),
            "execution_time": execution_time
        })
        
    except Exception as e:
        error_message = f"Error in search_similar_images: {str(e)}"
        print(error_message)
        print(f"Error type: {type(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )
        
    finally:
        print("Cleaning up temporary file...")
        try:
            if temp is not None:
                file.file.close()  # Close the uploaded file
                if os.path.exists(temp.name):
                    os.unlink(temp.name)  # Use os.unlink instead of os.remove
        except Exception as cleanup_error:
            print(f"Warning: Error during cleanup: {cleanup_error}")