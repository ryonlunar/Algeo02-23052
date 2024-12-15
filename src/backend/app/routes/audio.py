from fastapi import APIRouter
from mido import MidiFile, Message, MetaMessage
import os
import numpy as np
from typing import List, Tuple

def extract_melody(midi_path: str) -> List[int]:
    """Extract melody notes from MIDI file."""
    try:
        midi = MidiFile(midi_path)
        notes = []
        
        for track in midi.tracks:
            for msg in track:
                if (isinstance(msg, Message) and 
                    msg.type == 'note_on' and 
                    msg.velocity > 0 and 
                    msg.channel == 0):
                    notes.append(msg.note)
                    
                    # Limit the number of notes to prevent excessive processing
                    if len(notes) >= 1000:
                        return notes
        
        return notes
    except Exception as e:
        print(f"Error extracting melody from {midi_path}: {str(e)}")
        return []

def create_feature_vector(notes: List[int]) -> np.ndarray:
    """Create feature vector from notes using pitch histograms."""
    if not notes:
        return np.zeros(638)  # 128 + 255 + 255 total bins
        
    # Pitch histogram (ATB)
    pitch_hist, _ = np.histogram(notes, bins=128, range=(0, 128))
    pitch_hist = pitch_hist / (np.sum(pitch_hist) + 1e-8)
    
    # Interval histogram (RTB)
    intervals = np.diff(notes)
    interval_hist, _ = np.histogram(intervals, bins=255, range=(-127, 128))
    interval_hist = interval_hist / (np.sum(interval_hist) + 1e-8)
    
    # First-note relative histogram (FTB)
    if len(notes) > 0:
        first_note = notes[0]
        relative = np.array(notes) - first_note
        relative_hist, _ = np.histogram(relative, bins=255, range=(-127, 128))
        relative_hist = relative_hist / (np.sum(relative_hist) + 1e-8)
    else:
        relative_hist = np.zeros(255)
    
    # Combine features
    return np.concatenate([pitch_hist, interval_hist, relative_hist])

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return np.dot(v1, v2) / (norm1 * norm2)

def audio_retrieval_main(query_path: str, audio_folder: str, n: int = 10) -> Tuple[List[str], List[float]]:
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