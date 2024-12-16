from fastapi import APIRouter
from mido import MidiFile, Message, MetaMessage
import os
import numpy as np
from typing import List, Tuple

def extract_melody(midi_path: str) -> List[Tuple[int, int]]:
    """Extract melody notes from MIDI file."""
    try:
        midi = MidiFile(midi_path)
        notes = []
        current_time = 0
        
        for track in midi.tracks:
            for msg in track:
                current_time += msg.time
                
                if (isinstance(msg, Message) and 
                    msg.type == 'note_on' and 
                    msg.velocity > 0 and 
                    msg.channel == 0):
                    notes.append((current_time, msg.note))
                    
                    # Limit the number of notes to prevent excessive processing
                    if len(notes) >= 1000:
                        return notes
        
        return notes
    except Exception as e:
        print(f"Error extracting melody from {midi_path}: {str(e)}")
        return []
    
def normalize_melody(notes: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Normalize pitch in melody using z-score normalization."""
    pitches = [note[1] for note in notes]
    
    mean = np.mean(pitches)
    std = np.std(pitches)
    
    if std == 0:
        std = 1
        
    normalized_notes = [(note[0], (note[1] - mean) / std) for note in notes]
    
    return normalized_notes 

def windowing(normalized_notes: List[Tuple[int, int]], window_size: int = 40, window_slide: int = 8) -> List[List[Tuple[int, int]]]:
    """Apply sliding window technique to the melody."""
    windows = []
    
    # Ensure the number of notes is sufficient for windowing
    if len(normalized_notes) < window_size:
        print("Not enough notes to form a window. Returning empty list.")
        return windows
    
    # Slide the window over the melody with a given window size and step
    for i in range(0, len(normalized_notes) - window_size + 1, window_slide):
        window = normalized_notes[i:i + window_size]
        windows.append(window)

    return windows

def create_feature_vector(notes: List[Tuple[int, int]]) -> np.ndarray:
    """Create feature vector from notes using pitch histograms."""
    pitches = [note[1] for note in notes]
    
    if not pitches:
        return np.zeros(638)  # 128 + 255 + 255 total bins
        
    # Pitch histogram (ATB)
    atb_hist, _ = np.histogram(pitches, bins=128, range=(0, 128))
    atb_hist = atb_hist / (np.sum(atb_hist) + 1e-8)
    
    # Interval histogram (RTB)
    intervals = np.diff(pitches)
    rtb_hist, _ = np.histogram(intervals, bins=255, range=(-127, 128))
    rtb_hist = rtb_hist / (np.sum(rtb_hist) + 1e-8)
    
    # First-note relative histogram (FTB)
    if len(pitches) > 0:
        first_note = pitches[0]
        relative = np.array(pitches) - first_note
        ftb_hist, _ = np.histogram(relative, bins=255, range=(-127, 128))
        ftb_hist = ftb_hist / (np.sum(ftb_hist) + 1e-8)
    else:
        ftb_hist = np.zeros(255)
    
    # Combine features
    return np.concatenate([atb_hist, rtb_hist, ftb_hist])

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    magnitude1 = np.linalg.norm(v1)
    magnitude2 = np.linalg.norm(v2)
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return np.dot(v1, v2) / (magnitude1 * magnitude2)

def audio_retrieval_main(query_path: str, audio_folder: str, n: int = 30) -> Tuple[List[str], List[float]]:
    """Main function for audio retrieval."""
    try:
        print(f"Extracting query melody from {query_path}")
        query_notes = extract_melody(query_path)
        if not query_notes:
            raise ValueError("No valid notes found in query file")
            
        print("Creating query feature vector")
        query_vector = create_feature_vector(query_notes)
        
        print("Processing database files")
        similarities = []
        
        # Get all MIDI files
        midi_files = [f for f in os.listdir(audio_folder) if f.endswith('.mid')]
        total_files = len(midi_files)
        
        for i, filename in enumerate(midi_files, 1):
            if i % 10 == 0:
                print(f"Processing file {i}/{total_files}")
                
            full_path = os.path.join(audio_folder, filename)
            try:
                db_notes = extract_melody(full_path)
                if db_notes:
                    db_vector = create_feature_vector(db_notes)
                    similarity = cosine_similarity(query_vector, db_vector)
                    similarities.append((full_path, similarity))
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
        
        if not similarities:
            raise ValueError("No valid comparisons could be made")
            
        # Sort by similarity and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_n = similarities[:n]
        
        paths = [os.path.basename(path) for path, _ in top_n]
        scores = [score for _, score in top_n]
        
        return paths, scores
        
    except Exception as e:
        print(f"Error in audio retrieval: {str(e)}")
        raise