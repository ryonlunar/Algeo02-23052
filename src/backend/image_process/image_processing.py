import os
import cv2
import numpy as np

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
