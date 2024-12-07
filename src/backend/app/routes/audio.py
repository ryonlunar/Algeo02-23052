from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from mido import MidiFile
import numpy as np

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


def normalize_audio(melody):
    pitch = [note[0] for note in melody]
    mean = np.mean(pitch)
    std = np.std(pitch)
    normalized_pitch = [(note[0] - mean) / std if std > 0 else 0 for note in melody]
    
    return normalized_pitch

def audio_processing(audio_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file '{audio_path}' not found.")
    
    # Extract melody from audio path
    midi_data = MidiFile(audio_path)
    melodynotes = []
    
    for track in midi_data.tracks:
        time = 0
        for msg in track:
            time += msg.time
            
            if (msg.velocity > 0) and (msg.type == 'note_on') and (msg.channel == 0):
                melodynotes.append((msg.note, time))
    
    # Windowing melody
    windowing = []
    for i in range (0, len(melodynotes) - 20+1, 4):
        window = melodynotes[i:i + 20]
        windowing.append(window)
    
    # Normalize windows
    processed_windowing = [normalize_audio(window) for window in windowing]
    return processed_windowing

def extract_features_audio(pitches):
    # Extract ATB features
    atb_hist, _ = np.histogram(pitches, bins=128, range=(0, 127))
    if np.sum(atb_hist) > 0:
        atb = atb_hist / np.sum(atb_hist)
    else: atb = atb_hist
    
    # Extract RTB features
    interval = np.diff(pitches)
    rtb_hist, _ = np.histogram(interval, bins=255, range=(-127, 127))
    if np.sum(rtb_hist) > 0:
        rtb = rtb_hist / np.sum(rtb_hist)
    else: rtb = rtb_hist
    
    # Extract FTB features
    first_tone = pitches[0]
    differences = pitches - first_tone
    ftb_hist, _ = np.histogram(differences, bins=255, range=(-127,127))
    if np.sum(ftb_hist) > 0:
        ftb = ftb_hist / np.sum(ftb_hist)
    else: ftb = ftb_hist
    
    return atb, rtb, ftb

# To find cosine similarity between two vectors
def cosine_similarity(vector1, vector2):
    dot = np.dot(vector1, vector2)
    
    mag1 = np.linalg.norm(vector1)
    mag2 = np.linalg.norm(vector2)
    
    return dot / (mag1 * mag2)

# Main function that returns the top ten most similar audio in dataset
def audio_retrieval_main(query_audio, audio_folder, n=10):
    # Process query first
    query_window = audio_processing(query_audio)
    query_features = []
    for window in query_window:
        atb_query, rtb_query, ftb_query = extract_features_audio(window)
        query_features.append(np.concatenate(atb_query, rtb_query, ftb_query))
        
    song_paths = [os.path.join(audio_folder, f) for f in os.listdir(audio_folder) if f.endswith('.mid')]
    
    # Find the similarities between songs in dataset with query song
    similarities = []
    for song in song_paths:
        song_window = audio_processing(song)
        song_features = []
        for window in song_window:
            atb_song, rtb_song, ftb_song = extract_features_audio(window)
            song_features.append(np.concatenate(atb_song, rtb_song, ftb_song))
            
        avg_similarity = 0
        for query_feature in query_features:
            similarities_song = []
            for song_feature in song_features:
                similarity = cosine_similarity(query_feature, song_feature)
                similarities_song.append(similarity)
            avg_similarity += np.mean(similarities_song)
        
        avg_similarity /= len(query_features)
        similarities.append((song, avg_similarity))
        
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:n]