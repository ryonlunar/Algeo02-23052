import os
import cv2
import numpy as np
from scipy.spatial.distance import euclidean
from sklearn.decomposition import PCA

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

# Perhitungan PCA
def calculate_PCA(standardized_images, n):
    pca = PCA(n_components=n)
    pca.fit(standardized_images)
    return pca

def process_query(query_path, mean, pca, size):
    query_grayscale = convert_grayscale(query_path)
    query_resized = convert_size(query_grayscale, size)
    query_flattened = flatten(query_resized)
    query_std = query_flattened - mean
    query_projected = pca.transform([query_std])
    return query_projected[0]

def compute_similarity(query, dataset):
    distances = [euclidean(query, image) for image in dataset]
    sorted_distances = np.argsort(distances)
    return sorted_distances, distances

def image_retrieval(image_folder, query_path, n_components):
    base_array = image_processing(image_folder, (300, 300))
    standardized_images, mean_images = center_data(base_array)
    
    pca = calculate_PCA(standardized_images, n_components)
    projected_images = pca.transform(standardized_images)
    
    query_image = process_query(query_path, mean_images, pca, size=(300, 300))
    sorted_distances, distances = compute_similarity(query_image, projected_images)
    return sorted_distances, distances