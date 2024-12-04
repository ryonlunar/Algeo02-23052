import os
import numpy as np
from PIL import Image

def get_paths(folder):
    valid = ('.png', '.jpg', '.jpeg')
    
    paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(valid)]
    
    return paths

# Konversi gambar menjadi grayscale
def convert_grayscale(image_path):
    image = Image.open(image_path).convert('RGB')
    image_arr = np.array(image)
    
    if image_arr.shape[-1] == 4:
        image_arr = image_arr[:, :, :3]
        
    grayscale_arr = 0.2989 * image_arr[:, :, 0] + \
                    0.5870 * image_arr[:, :, 1] + \
                    0.1140 * image_arr[:, :, 2]
                    
    grayscale_image = Image.fromarray(grayscale_arr.astype('uint8'), mode="L")
    
    return grayscale_image

# Resize gambar
def resize_image(image, width, height):
    return image.resize((width, height), Image.Resampling.LANCZOS)

# Mengubah matrix gambar menjadi 1D
def flatten_image(image):
    image_arr = np.array(image)
    return image_arr.flatten()

# Fungsi untuk memroses gambar-gambar dari suatu dataset menjadi array 2D
def image_processing(image_folder, width, height):
    arr_images = []
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    for path in image_paths:
        grayscaled_image = convert_grayscale(path)
        resized_image = resize_image(grayscaled_image, width, height)
        flattened_image = flatten_image(resized_image)
        arr_images.append(flattened_image)
        
    return np.array(arr_images)

# Standarisasi data di sekitar nilai 0
def center_data(arr_images):
    mean_images = np.mean(arr_images, axis=0)
    arr_images_standardized = arr_images - mean_images
    return arr_images_standardized, mean_images

# Kalkulasi PCA menggunakan SVD
def compute_PCA(arr_images_standardized, n_components):
    U, S, Ut = np.linalg.svd(arr_images_standardized, full_matrices=False)
    
    top_component = Ut[:n_components]
    
    projected = np.dot(arr_images_standardized, top_component.T)
    
    return projected, top_component

# Proses query (grayscale, resize, dan flattening)
def preprocess_query(query_path, width, height):
    query_grayscale = convert_grayscale(query_path)
    query_resized = resize_image(query_grayscale, width, height)
    flatten_query = flatten_image(query_resized)
    
    return flatten_query

# Memproyeksi gambar query menjadi bentuk vector
def projected_query(flattened_query, mean, top_components):
    center_query = flattened_query - mean
    query = np.dot(center_query, top_components.T)
    
    return query

# Mengembalikan jarak Euclidean antara query dengan gambar
def euclidean_distance(query_vector, image_vector):
    return np.linalg.norm(query_vector - image_vector)

# Fungsi utama yang mengembalikan gambar-gambar paling mirip
# dan jarak Euclideannya
def image_retrieval_main(query_path, image_folder, n):
    width, height = 300, 300
    
    images_path = get_paths(image_folder)
    
    images_array = image_processing(image_folder, width, height)
    
    standardized_vector, mean_images = center_data(images_array)
    
    n_component = 50
    projected_vector, top_components = compute_PCA(standardized_vector, n_component)
    
    flattened_query = preprocess_query(query_path, width, height)
    
    proj_query = projected_query(flattened_query, mean_images, top_components)
    
    distances = np.array([euclidean_distance(proj_query, projected_vector[i]) for i in range(len(projected_vector))])
    
    sort_distances = np.argsort(distances)
    top_distances = sort_distances[:n]
    
    top_similar = [images_path[i] for i in top_distances]
    
    return top_similar, top_distances