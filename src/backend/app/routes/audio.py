from mido import MidiFile, Message, MetaMessage
import os
import numpy as np
from typing import List, Tuple
import threading

class ProcessController:
    def __init__(self):
        self.stop_event = threading.Event()
    
    def stop(self):
        self.stop_event.set()
        
    def is_stopped(self):
        return self.stop_event.is_set()

def extract_melody(midi_path: str, controller: ProcessController) -> List[int]:
    try:
        midi = MidiFile(midi_path)
        notes = []
        
        for track in midi.tracks:
            if controller.is_stopped():
                return []
                
            for msg in track:
                if controller.is_stopped():
                    return []
                    
                if (isinstance(msg, Message) and 
                    msg.type == 'note_on' and 
                    msg.velocity > 0 and 
                    msg.channel == 0):
                    notes.append(msg.note)
                    
                    if len(notes) >= 1000:
                        return notes
                        
        return notes
    except Exception as e:
        print(f"Error extracting melody from {midi_path}: {str(e)}")
        return []

def audio_retrieval_main(query_path: str, audio_folder: str, n: int = 10) -> Tuple[List[str], List[float]]:
    controller = ProcessController()
    
    try:
        print(f"Extracting query melody from {query_path}")
        query_notes = extract_melody(query_path, controller)
        if controller.is_stopped() or not query_notes:
            raise ValueError("Processing cancelled or no valid notes found")

        print("Creating query feature vector")
        query_vector = create_feature_vector(query_notes)
        
        print("Processing database files")
        similarities = []
        
        midi_files = [f for f in os.listdir(audio_folder) if f.endswith('.mid')]
        total_files = len(midi_files)
        
        for i, filename in enumerate(midi_files, 1):
            if controller.is_stopped():
                raise ValueError("Processing cancelled")
                
            if i % 10 == 0:
                print(f"Processing file {i}/{total_files}")
                
            full_path = os.path.join(audio_folder, filename)
            try:
                db_notes = extract_melody(full_path, controller)
                if controller.is_stopped():
                    raise ValueError("Processing cancelled")
                    
                if db_notes:
                    db_vector = create_feature_vector(db_notes)
                    similarity = cosine_similarity(query_vector, db_vector)
                    similarities.append((full_path, similarity))
            except Exception as e:
                if controller.is_stopped():
                    raise ValueError("Processing cancelled")
                print(f"Error processing {filename}: {str(e)}")
                continue
        
        if controller.is_stopped():
            raise ValueError("Processing cancelled")
            
        if not similarities:
            raise ValueError("No valid comparisons could be made")
            
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_n = similarities[:n]
        
        paths = [os.path.basename(path) for path, _ in top_n]
        scores = [score for _, score in top_n]
        
        return paths, np.array(scores)
        
    except Exception as e:
        print(f"Error in audio retrieval: {str(e)}")
        raise

def create_feature_vector(notes: List[int]) -> np.ndarray:
    if not notes:
        return np.zeros(638)
        
    pitch_hist, _ = np.histogram(notes, bins=128, range=(0, 128))
    pitch_hist = pitch_hist / (np.sum(pitch_hist) + 1e-8)
    
    intervals = np.diff(notes)
    interval_hist, _ = np.histogram(intervals, bins=255, range=(-127, 128))
    interval_hist = interval_hist / (np.sum(interval_hist) + 1e-8)
    
    if len(notes) > 0:
        first_note = notes[0]
        relative = np.array(notes) - first_note
        relative_hist, _ = np.histogram(relative, bins=255, range=(-127, 128))
        relative_hist = relative_hist / (np.sum(relative_hist) + 1e-8)
    else:
        relative_hist = np.zeros(255)
    
    return np.concatenate([pitch_hist, interval_hist, relative_hist])

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return np.dot(v1, v2) / (norm1 * norm2)