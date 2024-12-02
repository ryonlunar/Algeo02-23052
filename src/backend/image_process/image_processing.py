import os
import cv2
import numpy as np
from scipy.spatial.distance import euclidean

# Konversi gambar menjadi grayscale
def convert_grayscale(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

# Mengubah ukuran gambar agar seragam
def convert_size(image, size):
    return cv2.resize(image, size)

# Ubah vector grayscale menjadi 1D
def flatten(image):
    return image.flatten()

# Fungsi untuk memroses gambar-gambar dari suatu dataset
def image_processing(image_folder, size):
    arr_images = []
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    for path in image_paths:
        grayscaled_image = convert_grayscale(path)
        resized_image = convert_size(grayscaled_image, size)
        flattened_image = flatten(resized_image)
        arr_images.append(flattened_image)
        
    return np.array(arr_images)

# Standarisasi data di sekitar nilai 0
def center_data(arr_images):
    mean_images = np.mean(arr_images, axis=0)
    arr_images_standardized = arr_images - mean_images
    return arr_images_standardized, mean_images

# Perhitungan SVD
def calculate_SVD(data, n):
    U, S, Ut = np.linalg.svd(data, full_matrices=False)
    
    evec_component = Ut[:n] # Ambil n jumlah komponen utama teratas
    eval_component = S[:n] # Ambil n jumlah varian komponen utama teratas
    
    data_projection = np.dot(data, evec_component.T)
    
    return evec_component, eval_component, data_projection

def compute_similarity(query, dataset, Uk):
    query_projection = np.dot(query, Uk)
    dataset_projection = np.dot(dataset, Uk)
    
    # Cari jarak euclidean untuk tiap gambar
    distances = []
    for projection in dataset_projection:
        dist = euclidean(query_projection, projection)
        distances.append(dist)
    
    # Urutkan jarak euclidean
    sorted_distances = np.argsort(distances)
    
    return sorted_distances

